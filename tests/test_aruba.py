# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

# time format for Apr  5 22:51:54 2021
# <187>{{ arubadate }} {{ host }} authmgr[4130]: <124198> <4130> <ERRS> <{{ host }} 10.10.10.10>  {00:00:00:00:00:00-??} Missing server in attribute list, auth=VPN, utype=L3.
# <187>{{ arubadate }} {{ host }} stm[4133]: <399803> <4133> <ERRS> <{{ host }} 10.10.10.10>  An internal system error has occurred at file sapm_ap_mgmt.c function sapm_get_img_build_version_str line 11853 error stat /mswitch/sap/mips64.ari failed: No such file or directory.
# <188>{{ arubadate }} {{ host }} wms[4096]: <126005> <4096> <WARN> <{{ host }} 10.10.10.10> |ids| Interfering AP: The system classified an access point (BSSID 00:0e:8e:96:f4:32 and SSID  on CHANNEL 36) as interfering. Additional Info: Detector-AP-Name:00:0b:86:9e:6b:5f; Detector-AP-MAC:24:de:c6:70:2c:90; Detector-AP-Radio:1.
# <191>{{ arubadate }} 10.10.10.10 dnsmasq: reading /etc/resolv.conf

testdata = [
    "<187>{{ arubadate }} {{ host }} authmgr[4130]: <124198> <4130> <ERRS> <{{ host }} 10.10.10.10>  {00:00:00:00:00:00-??} Missing server in attribute list, auth=VPN, utype=L3.",
    "<187>{{ arubadate }} {{ host }} stm[4133]: <399803> <4133> <ERRS> <{{ host }} 10.10.10.10>  An internal system error has occurred at file sapm_ap_mgmt.c function sapm_get_img_build_version_str line 11853 error stat /mswitch/sap/mips64.ari failed: No such file or directory.",
    "<188>{{ arubadate }} {{ host }} wms[4096]: <126005> <4096> <WARN> <{{ host }} 10.10.10.10> |ids| Interfering AP: The system classified an access point (BSSID 00:0e:8e:96:f4:32 and SSID  on CHANNEL 36) as interfering. Additional Info: Detector-AP-Name:00:0b:86:9e:6b:5f; Detector-AP-MAC:24:de:c6:70:2c:90; Detector-AP-Radio:1.",
    "<188>{{ arubadate }} {{ host }} sapd[1362]: <127037> <WARN> |AP 00:0b:86:eb:4e:32@10.10.10.10 sapd| |ids-ap| AP(04:bd:88:8a:3a:60): Station Associated to Rogue AP: An AP detected a client a4:8d:3b:ae:68:68 associated to a rogue access point (BSSID 98:1e:19:31:63:b6 and SSID MySpectrumWiFib0-2G on CHANNEL 11).",
]


@pytest.mark.addons("aruba")
@pytest.mark.parametrize("event", testdata)
def test_aruba(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    arubadate = dt.strftime("%b %d %H:%M:%S %Y")

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<188>", bsd=bsd, host=host, arubadate=arubadate)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="aruba:syslog" host={{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

testdata_ossec = [
    "{{mark}}{{ bsd }} {{ host }} {{ app }}: Alert Level: 2; Rule: 1002 - Unknown problem somewhere in the system.; Location: so1->/var/log/messages; classification:  syslog,errors,; Oct  1 21:33:07 so1 amazon-ssm-agent: Error occurred fetching the seelog config file path:  open /etc/amazon/ssm/seelog.xml: no such file or directory",
    "{{mark}}{{ bsd }} {{ host }} {{ app }}: Alert Level: 3; Rule: 18145 - Service startup type was changed.; Location: (windows_os) 10.202.37.29->WinEvtLog; classification:  windows,policy_changed,; user: SYSTEM; 2020 Sep 28 02:33:16 WinEvtLog: System: INFORMATION(7040): Service Control Manager: SYSTEM: NT AUTHORITY: IP-0ACA251D: The start type of the Background Intelligent Transfer Service service was changed from auto start to demand start.",
    "{{mark}}{{ bsd }} {{ host }} {{ app }}: Alert Level: 3; Rule: 5502 - Login session closed.; Location: so1->/var/log/secure; classification:  pam,syslog,; Sep 25 10:12:15 so1 sshd[3201]: pam_unix(sshd:session): session closed for user splunker",
    "{{mark}}{{ bsd }} {{ host }} {{ app }}: Alert Level: 7; Rule: 552 - Integrity checksum changed again (3rd time).; Location: so1->syscheck; classification: ossec,syscheck,; Previous MD5: '3e244ac47c346cc252f093a4e4f000fb'; Current MD5: 'd9ba8c6e3f0da05a67e24ac00668b6cc'; Previous SHA1: '116719c7294da657ff936b5676a82e6bf18a5a28'; Current SHA1: '1b1f0eaa6884e8398fd6ab92d9ebd96705d00a6b'; Size changed: from '409' to '446'; Integrity checksum changed for: '/etc/firewalld/zones/public.xml'",
]


@pytest.mark.addons("ossec")
@pytest.mark.parametrize("event", testdata_ossec)
def test_data_ossec(record_property,  setup_splunk, setup_sc4s, event):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<132>", bsd=bsd, host=host, app="ossec")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=main _time={{ epoch }} sourcetype="ossec" source="ossec:alerts" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="ossec")
    message1 = message1.lstrip()
    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

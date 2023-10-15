# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# https://www.ciscolive.com/c/dam/r/ciscolive/us/docs/2017/pdf/TECUCC-3000.pdf

# <111> Mar 17 18:35:12 xyz_vManage_West SYSMGR[919]: %Viptela-xyz_vManage_East-sysmgrd-6-INFO-1400002: Notification: 3/17/2022 18:35:12 system-login-change severity-level:minor host-name:"XYZ_vManage_East" system-ip:1.1.1.3 user-name:"mn2c" user-id:2227


@pytest.mark.addons("cisco")
def test_cisco_viptela(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} SYSMGR[919]: %Viptela-{{ host }}-sysmgrd-6-INFO-1400002: Notification: 3/17/2022 18:35:12 system-login-change severity-level:minor host-name:"{{ host }}" system-ip:1.1.1.3 user-name:"mn2c" user-id:2227\n'
    )
    message = mt.render(mark="<189>", tzname=tzname, bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host={{ host }} sourcetype="cisco:viptela"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

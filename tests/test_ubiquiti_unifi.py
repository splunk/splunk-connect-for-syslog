# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <27>Nov  8 17:28:43 US8P60,18e8294876c3,v4.0.66.10832 switch: DOT1S: dot1sBpduReceive(): Discarding the BPDU on port 0/7, since it is an invalid BPDU type

@pytest.mark.addons("ubiquiti")
def test_ubiquiti_unifi_us8p60(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} {{key}},18e8294876c3,v4.0.66.10832 switch: DOT1S: dot1sBpduReceive(): Discarding the BPDU on port 0/7, since it is an invalid BPDU type "
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype=ubnt host="{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <29>Nov 10 20:46:02 US24P250,f09fc26f4419,v4.0.54.10625 switch: TRAPMGR: Cold Start: Unit: 0
@pytest.mark.addons("ubiquiti")
def test_ubiquiti_unifi_switch_us24p250(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} {{key}},f09fc26f4419,v4.0.54.10625 switch: TRAPMGR: Cold Start: Unit: "
    )
    message = mt.render(mark="<27>", bsd=bsd, key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype=ubnt host="{{key}}"'
    )
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <30>Nov 10 11:49:46 U7PG2,788a2056b181,v4.0.66.10832: logread[5495]: Logread connected to 10.2.0.9:514
@pytest.mark.addons("ubiquiti")
def test_ubiquiti_unifi_ap_u7pg2(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} U7PG2,788a2056b182,v4.0.66.10832: logread[5495]: Logread connected to 10.1.1.1:514 {{ host }}"
    )
    message = mt.render(mark="<27>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype=ubnt NOT host=U7PG2 788a2056b182 "{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <30>Nov 10 11:49:46 U7PG2,788a2056b181,v4.0.66.10832: logread[5495]: Logread connected to 10.2.0.9:514
@pytest.mark.addons("ubiquiti")
def test_ubiquiti_unifi_ap_u7pg2_alt(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} 788a2056b183,v4.0.66.10832: logread[5495]: Logread connected to 10.2.0.9:514 {{ host }}"
    )
    message = mt.render(mark="<27>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype=ubnt NOT host=U7PG2 NOT host={{ host }} 788a2056b183 "{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <4>Nov 10 23:04:06 USG kernel: [LAN_LOCAL-default-A]IN=eth0.2004 OUT= MAC= SRC=10.254.3.1 DST=224.0.0.251 LEN=348 TOS=0x00 PREC=0x00 TTL=255 ID=32463 DF PROTO=UDP SPT=5353 DPT=5353 LEN=328
@pytest.mark.addons("ubiquiti")
def test_ubiquiti_unifi_usg(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} usg-{{host}} kernel: [LAN_LOCAL-default-A]IN=eth0.2004 OUT= MAC= SRC=10.254.3.1 DST=224.0.0.251 LEN=348 TOS=0x00 PREC=0x00 TTL=255 ID=32463 DF PROTO=UDP SPT=5353 DPT=5353 LEN=328"
    )
    message = mt.render(mark="<27>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        "search _time={{ epoch }} index=netfw sourcetype=ubnt:fw host=usg-{{host}}"
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

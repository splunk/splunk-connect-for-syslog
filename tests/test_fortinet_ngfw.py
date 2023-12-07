# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations, insert_char
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <111> Aug 17 00:00:00 fortigate date=2015-08-11 time=19:19:43 devname=Nosey devid=FG800C3912801080 logid=0004000017 type=traffic subtype=sniffer level=notice vd=root srcip=fe80::20c:29ff:fe77:20d4 srcintf="port3" dstip=ff02::1:ff77:20d4 dstintf="port3" sessionid=408903 proto=58 action=accept policyid=2 dstcountry="Reserved" srccountry="Reserved" trandisp=snat transip=:: transport=0 service="icmp6/131/0" duration=36 sentbyte=0 rcvdbyte=40 sentpkt=0 rcvdpkt=0 appid=16321 app="IPv6.ICMP" appcat="Network.Service" apprisk=elevated applist="sniffer-profile" appact=detected utmaction=allow countapp=1
@pytest.mark.addons("fortinet")
def test_fortinet_fgt_event(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-7]

    mt = env.from_string(
        #       "{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} devid=FGT60D4614044725 logid=0100040704 type=event subtype=system level=notice tz=\"{{ tzoffset }}\" vd=root logdesc=\"System performance statistics\" action=\"perf-stats\" cpu=2 mem=35 totalsession=61 disk=2 bandwidth=158/138 setuprate=2 disklograte=0 fazlograte=0 msg=\"Performance statistics: average CPU: 2, memory:  35, concurrent sessions:  61, setup-rate: 2\"\n")
        '{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} devid=FGT60D4614044725 logid=0100040704 type=event subtype=system level=notice vd=root logdesc="System performance statistics" action="perf-stats" cpu=2 mem=35 totalsession=61 disk=2 bandwidth=158/138 setuprate=2 disklograte=0 fazlograte=0 msg="Performance statistics: average CPU: 2, memory:  35, concurrent sessions:  61, setup-rate: 2"\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="fgt_event"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <111> Aug 17 00:00:00 fortigate date=2015-08-11 time=19:19:43 devname=Nosey devid=FG800C3912801080 logid=0004000017 type=traffic subtype=sniffer level=notice vd=root srcip=fe80::20c:29ff:fe77:20d4 srcintf="port3" dstip=ff02::1:ff77:20d4 dstintf="port3" sessionid=408903 proto=58 action=accept policyid=2 dstcountry="Reserved" srccountry="Reserved" trandisp=snat transip=:: transport=0 service="icmp6/131/0" duration=36 sentbyte=0 rcvdbyte=40 sentpkt=0 rcvdpkt=0 appid=16321 app="IPv6.ICMP" appcat="Network.Service" apprisk=elevated applist="sniffer-profile" appact=detected utmaction=allow countapp=1
@pytest.mark.addons("fortinet")
def test_fortinet_fgt_traffic(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} devid=FG800C3912801080 logid=0004000017 type=traffic subtype=sniffer level=notice vd=root srcip=fe80::20c:29ff:fe77:20d4 srcintf="port3" dstip=ff02::1:ff77:20d4 dstintf="port3" sessionid=408903 proto=58 action=accept policyid=2 dstcountry="Reserved" srccountry="Reserved" trandisp=snat transip=:: transport=0 service="icmp6/131/0" duration=36 sentbyte=0 rcvdbyte=40 sentpkt=0 rcvdpkt=0 appid=16321 app="IPv6.ICMP" appcat="Network.Service" apprisk=elevated applist="sniffer-profile" appact=detected utmaction=allow countapp=1\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="fgt_traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <111> Aug 17 00:00:00 fortigate date=2015-08-11 time=19:21:40 logver=52 devname=US-Corp_Main1 devid=FGT37D4613800138 logid=0317013312 type=utm subtype=webfilter eventtype=ftgd_allow level=notice vd=root sessionid=1490845588 user="" srcip=172.30.16.119 srcport=53235 srcintf="Internal" dstip=114.112.67.75 dstport=80 dstintf="External-SDC" proto=6 service=HTTP hostname="popo.wan.ijinshan.com" profile="scan" action=passthrough reqtype=direct url="/popo/launch?c=cHA9d29vZHMxOTgyQGhvdG1haWwuY29tJnV1aWQ9NDBiNDkyZDRmNzdhNjFmOTNlMjQwMjhiYjE3ZGRlYTYmY29tcGl" sentbyte=525 rcvdbyte=325 direction=outgoing msg="URL belongs to an allowed category in policy" method=domain cat=52 catdesc="Information Technology"
@pytest.mark.addons("fortinet")
def test_fortinet_fgt_utm(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} devid=FGT37D4613800138 logid=0317013312 type=utm subtype=webfilter eventtype=ftgd_allow level=notice vd=root sessionid=1490845588 user="" srcip=172.30.16.119 srcport=53235 srcintf="Internal" dstip=114.112.67.75 dstport=80 dstintf="External-SDC" proto=6 service=HTTP hostname="popo.wan.ijinshan.com" profile="scan" action=passthrough reqtype=direct url="/popo/launch?c=cHA9d29vZHMxOTgyQGhvdG1haWwuY29tJnV1aWQ9NDBiNDkyZDRmNzdhNjFmOTNlMjQwMjhiYjE3ZGRlYTYmY29tcGl" sentbyte=525 rcvdbyte=325 direction=outgoing msg="URL belongs to an allowed category in policy" method=domain cat=52 catdesc="Information Technology"\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="fgt_utm"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <111> date=2015-08-11 time=19:19:43 devname=Nosey devid=FG800C3912801080 logid=0004000017 type=traffic subtype=sniffer level=notice vd=root srcip=fe80::20c:29ff:fe77:20d4 srcintf="port3" dstip=ff02::1:ff77:20d4 dstintf="port3" sessionid=408903 proto=58 action=accept policyid=2 dstcountry="Reserved" srccountry="Reserved" trandisp=snat transip=:: transport=0 service="icmp6/131/0" duration=36 sentbyte=0 rcvdbyte=40 sentpkt=0 rcvdpkt=0 appid=16321 app="IPv6.ICMP" appcat="Network.Service" apprisk=elevated applist="sniffer-profile" appact=detected utmaction=allow countapp=1
@pytest.mark.addons("fortinet")
def test_fortinet_fgt_traffic_framed(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}date={{ date }} time={{ time }} devname={{ host }} devid=FG800C3912801080 logid=0004000017 type=traffic subtype=sniffer level=notice vd=root srcip=fe80::20c:29ff:fe77:20d4 srcintf="port3" dstip=ff02::1:ff77:20d4 dstintf="port3" sessionid=408903 proto=58 action=accept policyid=2 dstcountry="Reserved" srccountry="Reserved" trandisp=snat transip=:: transport=0 service="icmp6/131/0" duration=36 sentbyte=0 rcvdbyte=40 sentpkt=0 rcvdpkt=0 appid=16321 app="IPv6.ICMP" appcat="Network.Service" apprisk=elevated applist="sniffer-profile" appact=detected utmaction=allow countapp=1\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset
    )
    message_len = len(message)
    ietf = f"{message_len} {message}"

    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="fgt_traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("fortinet")
def test_fortinet_fgt_traffic_nohdr(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}date={{ date }} time={{ time }} devname={{ host }} devid=FG800C3912801080 logid=0004000017 type=traffic subtype=sniffer level=notice vd=root srcip=fe80::20c:29ff:fe77:20d4 srcintf="port3" dstip=ff02::1:ff77:20d4 dstintf="port3" sessionid=408903 proto=58 action=accept policyid=2 dstcountry="Reserved" srccountry="Reserved" trandisp=snat transip=:: transport=0 service="icmp6/131/0" duration=36 sentbyte=0 rcvdbyte=40 sentpkt=0 rcvdpkt=0 appid=16321 app="IPv6.ICMP" appcat="Network.Service" apprisk=elevated applist="sniffer-profile" appact=detected utmaction=allow countapp=1\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset
    )
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="fgt_traffic"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("fortinet")
def test_fortinet_fgt_event_et_epoch(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-7]

    mt = env.from_string(
        #       "{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} devid=FGT60D4614044725 logid=0100040704 type=event subtype=system level=notice tz=\"{{ tzoffset }}\" vd=root logdesc=\"System performance statistics\" action=\"perf-stats\" cpu=2 mem=35 totalsession=61 disk=2 bandwidth=158/138 setuprate=2 disklograte=0 fazlograte=0 msg=\"Performance statistics: average CPU: 2, memory:  35, concurrent sessions:  61, setup-rate: 2\"\n")
        '{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} eventtime={{ epoch }} devid=FGT60D4614044725 logid=0100040704 type=event subtype=system level=notice vd=root logdesc="System performance statistics" action="perf-stats" cpu=2 mem=35 totalsession=61 disk=2 bandwidth=158/138 setuprate=2 disklograte=0 fazlograte=0 msg="Performance statistics: average CPU: 2, memory:  35, concurrent sessions:  61, setup-rate: 2"\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset, epoch=epoch
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="fgt_event"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("fortinet")
def test_fortinet_fgt_event_et_epochms(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Fortigate
    time = time[:-7]
    tzoffset = insert_char(tzoffset, ":", 3)
    epoch = epoch[:-3]

    mt = env.from_string(
        #       "{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} devid=FGT60D4614044725 logid=0100040704 type=event subtype=system level=notice tz=\"{{ tzoffset }}\" vd=root logdesc=\"System performance statistics\" action=\"perf-stats\" cpu=2 mem=35 totalsession=61 disk=2 bandwidth=158/138 setuprate=2 disklograte=0 fazlograte=0 msg=\"Performance statistics: average CPU: 2, memory:  35, concurrent sessions:  61, setup-rate: 2\"\n")
        '{{ mark }} {{ bsd }} fortigate date={{ date }} time={{ time }} devname={{ host }} eventtime={{ epoch }} devid=FGT60D4614044725 logid=0100040704 type=event subtype=system level=notice vd=root logdesc="System performance statistics" action="perf-stats" cpu=2 mem=35 totalsession=61 disk=2 bandwidth=158/138 setuprate=2 disklograte=0 fazlograte=0 msg="Performance statistics: average CPU: 2, memory:  35, concurrent sessions:  61, setup-rate: 2"\n'
    )
    message = mt.render(
        mark="<111>", bsd=bsd, date=date, time=time, host=host, tzoffset=tzoffset, epoch=epoch
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="fgt_event"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

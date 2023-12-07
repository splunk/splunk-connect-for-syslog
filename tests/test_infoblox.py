# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import shortuuid
import pytz
import pytest

from jinja2 import Environment, select_autoescape, environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


infoblox_dns_testdata = [
    r'{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: Recursion cache view "_default": size = 89496, hits = 1, misses = 3',
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: 24-Sep-2020 09:46:27.205 client 192.168.1.3#61567: UDP: query: 2.1.168.192.in-addr.arpa IN PTR response: NXDOMAIN +",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: 24-Sep-2020 09:46:27.329 client 192.168.1.3#61568: UDP: query: abc.com IN A response: NOERROR + abc.com. 60 IN A 13.32.86.14; abc.com. 60 IN A 13.32.86.89; abc.com. 60 IN A 13.32.86.7; abc.com. 60 IN A 13.32.86.42;",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: 24-Sep-2020 09:46:27.336 client 192.168.1.3#61569: UDP: query: abc.com IN AAAA response: NOERROR +",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c74087120 192.168.1.3#61568 (abc.com): query: abc.com IN A + (192.168.1.2)",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c840cc860 192.168.1.3#61567 (2.1.168.192.in-addr.arpa): query: 2.1.168.192.in-addr.arpa IN PTR + (192.168.1.2)",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c840cc860 192.168.1.3#61567 (2.1.168.192.in-addr.arpa): RFC 1918 response from Internet for 2.1.168.192.in-addr.arpa",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: client @0x7f0c840cc860 192.168.1.3#61569 (abc.com): query: abc.com IN AAAA + (192.168.1.2)",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: FORMERR resolving 'www.google.com/AAAA/IN': 209.2.230.6#53",
    r"{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: Recursion client quota: used/max/soft-limit/s-over/hard-limit/h-over/low-pri = 0/1/900/0/1000/0/0",
]

infoblox_dhcp_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: Abandoning IP address 192.168.1.125: pinged before offer",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPACK on 192.168.1.120 to 00:50:56:13:60:56 (dummyhost) via eth1 relay eth1 lease-duration 600 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPDISCOVER from 00:50:56:13:60:56 via eth1 TransID c02c6bb8 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPEXPIRE on 192.168.1.125 to 00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPOFFER on 192.168.1.120 to 00:50:56:13:60:56 (dummyhost) via eth1 relay eth1 lease-duration 119 offered-duration 600 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPRELEASE of 192.168.1.126 from 00:50:56:13:60:56 (dummyhost) via eth1 (found) TransID 8554a358 uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPREQUEST for 10.130.151.62 from 80:ce:62:9c:0e:70 (DTCCE0826E00C97) via eth2 TransID 802c562c uid 01:80:ce:62:9c:0e:70 (RENEW)",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: DHCPREQUEST for 192.168.1.120 (192.168.1.2) from 00:50:56:13:60:56 (dummyhost) via eth1 TransID 9a5fbd6e uid 01:00:50:56:13:60:56",
    r"{{ mark }}{{ bsd }} {{ host }} dhcpd[{{ pid }}]: uid lease 192.168.1.125 for client 00:50:56:13:60:56 is duplicate on 192.168.1.0/24",
]

infoblox_alterheader_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} 10.0.0.1 dhcpd[{{ pid }}]: Abandoning IP address 192.168.1.125: pinged before offer",
]
infoblox_threatprotect_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} threat-protect-log[31782]: [32080] <notice> -- Rule Upload start",
    r"{{ mark }}{{ bsd }} {{ host }} threat-protect-log: [8943] <notice> -- total signatures reordered by the sigordering module: 431",
    r"{{ mark }}{{ bsd }} {{ host }} threat-protect-log: [8943] <notice> -- Total Signatures to be processed by thesigordering module: 431",
    r"{{ mark }}{{ bsd }} {{ host }} threat-protect-log: [8943] <notice> -- version:SW_ATP-3.2.3-4.3 Infoblox-APR 28, 2019 ",
]

infoblox_audit_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} -serial_console: 2020-09-24 09:35:04.751Z [admin]: Logout - - ip=10.1.1.3 group=.admin-group trigger_event=Session\040Expiration",
    r"{{ mark }}{{ bsd }} {{ host }} -serial_console: 2020-09-24 10:29:43.024Z [USER\040admin]: rotated the previous audit log to audit.log.0.gz",
    r"{{ mark }}{{ bsd }} {{ host }} serial_console: 2020-09-16 13:22:51.992Z [root]: Login_Denied - - to=Serial\040Console apparently_via=Direct error=invalid\040login\040or\040password",
    r"{{ mark }}{{ bsd }} {{ host }} serial_console: 2020-09-16 13:28:56.612Z [USER\040admin]: rebooted the system",
    r'{{ mark }}{{ bsd }} {{ host }} serial_console: 2020-09-17 07:14:58.037Z [admin]: Called - set_temp_license: Args temp_license="Response Policy Zones license for 60 days",grid_wide=True',
    r"{{ mark }}{{ bsd }} {{ host }} sshd[1066]: 2020-09-16 14:12:35.990Z [root]: Login_Denied - - apparentlyi_via=Remote ip=2.57.122.204 auth=PAM",
    r'{{ mark }}{{ bsd }} {{ host }} httpd: 2020-09-24 11:44:48.352Z [admin]: Called - GetLogFiles message=downloaded\040syslog: Args message="downloaded syslog"',
    r"{{ mark }}{{ bsd }} {{ host }} httpd: 2020-09-24 11:56:27.281Z [admin]: Logout - - ip=10.1.1.3 group=admin-group trigger_event=Session\040Expiration",
    r"{{ mark }}{{ bsd }} {{ host }} httpd: 2020-09-24 13:31:18.634Z [admin2]: Login_Allowed - - to=AdminConnector ip=192.168.1.3 auth=LOCAL group=admin-group apparently_via=GUI",
]

infoblox_fallback_testdata = [
    r"{{ mark }}{{ bsd }} {{ host }} kernel: : [158316.604054] EXT4-fs (sda4): re-mounted. Opts: barrier=0",
    r"{{ mark }}{{ bsd }} {{ host }} debug_mount: mount -o remount,ro /dev/sda4 < /bin/sh/infoblox/rcrestart < init",
    r"{{ mark }}{{ bsd }} {{ host }} monitor[19707]: Type: clusterd, State: Red, Event: A grid daemon failure has occurred. ",
    r"{{ mark }}{{ bsd }} {{ host }} logger: ARP on passive HA interface is disabled.",
    r"{{ mark }}{{ bsd }} {{ host }} ntpd[18544]: Listening on routing socket on fd #22 for interface updates",
    r"{{ mark }}{{ bsd }} {{ host }} python: Success : File download success for atp update and it is rsync with GM.",
    r'{{ mark }}{{ bsd }} {{ host }} python: Threat protection rule update: Reading ruleset revision:"20200916", version:"10".',
    r"{{ mark }}{{ bsd }} {{ host }} -serial_console: User group = admin-group4",
    r"{{ mark }}{{ bsd }} {{ host }} watchdog: CLIENT received SIGTERM, cancelling softdog and exiting...",
    r"{{ mark }}{{ bsd }} {{ host }} rc6: sending the TERM signal to watchdog",
]


# <30>Sep 18 10:46:16 10.1.1.2 named[23276]: CEF:0|Infoblox|NIOS|8.4.4-386831|RPZ-QNAME|NXDOMAIN|7|app=DNS dst=192.168.1.2 src=10.1.1.3 spt=65498 view=_default qtype=AAAA msg="rpz QNAME NXDOMAIN rewrite www.aaaaa.com [AAAA] via www.aaaaa.com.local-rpz" CAT=RPZ
@pytest.mark.addons("infoblox")
def test_infoblox_dns_rpz_cef(
    record_property,  setup_splunk, setup_sc4s, get_pid
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} named[{{ pid }}]: CEF:0|Infoblox|NIOS|8.4.4-386831|RPZ-QNAME|NXDOMAIN|7|app=DNS dst=192.168.1.2 src=10.1.1.3 spt=65498 view=_default qtype=AAAA msg="rpz QNAME NXDOMAIN rewrite www.aaaaa.com [AAAA] via www.aaaaa.com.local-rpz" CAT=RPZ'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netdns host={{ host }} sourcetype="infoblox:dns"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("infoblox")
@pytest.mark.parametrize("event", infoblox_dns_testdata)
def test_infoblox_dns(record_property,  setup_splunk, setup_sc4s, get_pid, event):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netdns host={{ host }} sourcetype="infoblox:dns"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("infoblox")
@pytest.mark.parametrize("event", infoblox_dhcp_testdata)
def test_infoblox_dhcp(
    record_property,  setup_splunk, setup_sc4s, get_pid, event
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<150>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netipam host={{ host }} sourcetype="infoblox:dhcp"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <27>Sep 17 13:23:11 10.1.1.2 threat-protect-log[21962]: CEF:0|Infoblox|NIOS Threat|8.4.4-386831|120303001|Blacklist:foo.foo.foo|7|src=192.168.1.3 spt=57092 dst=192.168.1.2 dpt=53 act="DROP" cat="BLACKLIST UDP FQDN lookup" nat=0 nfpt=0 nlpt=0 fqdn=foo.foo.foo hit_count=4
@pytest.mark.addons("infoblox")
def test_infoblox_dns_threatprotect_cef(
    record_property,  setup_splunk, setup_sc4s, get_pid
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} threat-protect-log[{{ pid }}]: CEF:0|Infoblox|NIOS Threat|8.4.4-386831|120303001|Blacklist:foo.foo.foo|7|src=192.168.1.3 spt=57092 dst=192.168.1.2 dpt=53 act="DROP" cat="BLACKLIST UDP FQDN lookup" nat=0 nfpt=0 nlpt=0 fqdn=foo.foo.foo hit_count=4'
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host={{ host }} sourcetype="infoblox:threatprotect"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("infoblox")
@pytest.mark.parametrize("event", infoblox_threatprotect_testdata)
def test_infoblox_dns_threatprotect(
    record_property,  setup_splunk, setup_sc4s, get_pid, event
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host={{ host }} sourcetype="infoblox:threatprotect"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("infoblox")
@pytest.mark.parametrize("event", infoblox_audit_testdata)
def test_infoblox_audit(
    record_property,  setup_splunk, setup_sc4s, get_pid, event
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host={{ host }} sourcetype="infoblox:audit"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("infoblox")
@pytest.mark.parametrize("event", infoblox_fallback_testdata)
def test_infoblox_fallback(
    record_property,  setup_splunk, setup_sc4s, get_pid, event
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<13>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host={{ host }} sourcetype="infoblox:port"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("infoblox")
@pytest.mark.parametrize("event", infoblox_alterheader_testdata)
def test_infoblox_headeralter_dhcp(
    record_property,  setup_splunk, setup_sc4s, get_pid, event
):
    host = f"infoblox-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<150>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netipam host={{ host }} sourcetype="infoblox:dhcp"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

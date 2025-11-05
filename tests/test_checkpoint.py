# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
import pytest

from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


#
# Oct 8 15:00:25 DEVICENAME time=1570561225|hostname=devicename|severity=Informational|confidence_level=Unknown|product=IPS|action=Drop|ifdir=inbound|ifname=bond2|loguid={0x5d9cdcc9,0x8d159f,0x5f19f392,0x1897a828}|origin=1.1.1.1|time=1570561225|version=1|attack=Streaming Engine: TCP Segment Limit Enforcement|attack_info=TCP segment out of maximum allowed sequence. Packet dropped.|chassis_bladed_system=[ 1_3 ]|dst=10.10.10.10|origin_sic_name=CN=something_03_local,O=devicename.domain.com.p7fdbt|performance_impact=0|protection_id=tcp_segment_limit|protection_name=TCP Segment Limit Enforcement|protection_type=settings_tcp|proto=6|rule=393|rule_name=10.384_..|rule_uid={9F77F944-8DD5-4ADF-803A-785D03B3A2E8}|s_port=46455|service=443|smartdefense_profile=Recommended_Protection_ded9e8d8ee89d|src=1.1.1.2|
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_ips(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|severity=Informational|confidence_level=Unknown|product=IPS|action=Drop|ifdir=inbound|ifname=bond2|loguid={{ host }}{0x5d9cdcc9,0x8d159f,0x5f19f392,0x1897a828}|origin=1.1.1.1|time={{ epoch }}|version=1|attack=Streaming Engine: TCP Segment Limit Enforcement|attack_info=TCP segment out of maximum allowed sequence. Packet dropped.|chassis_bladed_system=[ 1_3 ]|dst=10.10.10.10|origin_sic_name=CN={{ host }},O=devicename.domain.com.p7fdbt|performance_impact=0|protection_id=tcp_segment_limit|protection_name=TCP Segment Limit Enforcement|protection_type=settings_tcp|proto=6|rule=393|rule_name=10.384_..|rule_uid={9F77F944-8DD5-4ADF-803A-785D03B3A2E8}|s_port=46455|service=443|smartdefense_profile=Recommended_Protection_ded9e8d8ee89d|src=1.1.1.2|\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}-lm" sourcetype="cp_log" source="checkpoint:ids"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# $Oct 8 15:48:31 DEVICENAME time=1570564111|hostname=devicename|product=Firewall|action=Drop|ifdir=inbound|ifname=bond1|loguid={0x5d9ce80f,0x8d0555,0x5f19f392,0x18982828}|origin=1.1.1.1|time=1570564111|version=1|chassis_bladed_system=[ 1_1 ]|dst=10.10.10.10|inzone=External|origin_sic_name=CN=something_03_local,O=devicename.domain.com.p7fdbt|outzone=Internal|proto=6|rule=402|rule_name=11_..|rule_uid={C8CD796E-7BD5-47B6-90CA-B250D062D5E5}|s_port=33687|service=23|src=1.1.1.2|
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_firewall(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|product=Firewall|action=Drop|ifdir=inbound|ifname=bond1|loguid={{ host }}{0x5d9ce80f,0x8d0555,0x5f19f392,0x18982828}|origin=1.1.1.1|time={{ epoch }}|version=1|chassis_bladed_system=[ 1_1 ]|dst=10.10.10.10|inzone=External|origin_sic_name=CN={{ host }},O=devicename.domain.com.p7fdbt|outzone=Internal|proto=6|rule=402|rule_name=11:..|rule_uid={C8CD796E-7BD5-47B6-90CA-B250D062D5E5}|s_port=33687|service=23|src=1.1.1.2|\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}-lm" sourcetype="cp_log" source="checkpoint:firewall"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_firewall_noise(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|product=Firewall|action=Drop|ifdir=inbound|ifname=bond1|loguid={{ host }}-{0x5d9ce80f,0x8d0555,0x5f19f392,0x18982828}|origin=1.1.1.1|time={{ epoch }}|version=1|chassis_bladed_system=[ 1_1 ]|dst=10.10.10.10|inzone=External|origin_sic_name=CN={{ host }},O=devicename.domain.com.p7fdbt|outzone=Internal|proto=6|rule=402|rule_name=11:..|rule_uid={C8CD796E-7BD5-47B6-90CA-B250D062D5E5}|s_port=33687|service=23|src=1.1.1.2|\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}-lm" sourcetype="cp_log"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_firewall2(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|severity=Medium|product=Firewall|action=Drop|ifdir=inbound|ifname=eth1|loguid={{ host }}{0x0,0x0,0x0,0x1}|origin=111.89.111.53|originsicname=CN\={{ host }},O\=cma-xx.xx.net.xx|sequencenum=64|time={{epoch}}|version=5|dst=10.11.11.11|inspection_category=anomaly|foo=bar: bat mark||\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}-lm" sourcetype="cp_log" source="checkpoint:firewall"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("checkpoint")
def test_checkpoint_vsplunk_firewall(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|severity=Medium|product=Firewall|action=Drop|ifdir=inbound|ifname=eth1|loguid={{ host }}{0x0,0x0,0x0,0x2}|origin=111.89.111.53|originsicname=CN\=blah-v_{{ host }},O\=cma-xx.xx.net.xx|sequencenum=64|time={{epoch}}|version=5|dst=10.11.11.11|inspection_category=anomaly|foo=bar: bat mark||\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}-lm" sourcetype="cp_log" source="checkpoint:firewall"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Oct  9 12:01:16 DEVICENAME |hostname=DEVICENAME|product=mds-query-tool|action=Accept|ifdir=outbound|origin=1.1.1.1|2.2.2.2|originsicname=cn\=cp_mgmt,o\=DEVICENAME.domain.com.p7fdbt|sequencenum=1|time=1570641309|version=5|administrator=localhost|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log Out|operation_number=12|subject=Administrator Login|
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_mds(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|product=mds-query-tool|action=Accept|ifdir=outbound|origin=1.1.1.1|2.2.2.2|originsicname=cn\={{ host }},o\=DEVICENAME.domain.com.p7fdbt|sequencenum=1|version=5|administrator=localhost|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log Out|operation_number=12|subject=Administrator Login|\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}-lm" sourcetype="cp_log"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Oct  9 12:01:16 DEVICENAME |hostname=DEVICENAME|product=CPMI Client|action=Accept|ifdir=outbound|origin=1.1.1.1|2.2.2.2|originsicname=cn\=cp_mgmt,o\=DEVICENAME.domain.com.p7fdbt|sequencenum=1|time=1570641173|version=5|administrator=localhost|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log Out|operation_number=12|subject=Administrator Login
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_cpmi(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|product=CPMI Client|action=Accept|ifdir=outbound|origin=1.1.1.1|2.2.2.2|originsicname=cn\={{ host }},o\=DEVICENAME.domain.com.p7fdbt|sequencenum=1|version=5|administrator=localhost|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log Out|operation_number=12|subject=Administrator Login\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}-lm" sourcetype="cp_log"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Oct  9 12:01:16 DEVICENAME |hostname=DEVICENAME|product=WEB_API|action=Accept|ifdir=outbound|origin=1.1.1.1|2.2.2.2|originsicname=cn\=cp_mgmt,o\=DEVICENAME.domain.com.p7fdbt|sequencenum=1|time=1570640578|version=5|administrator=tufinapi|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log Out|operation_number=12|subject=Administrator Login
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_web_api(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}-lm|product=WEB_API|action=Accept|ifdir=outbound|origin=1.1.1.1|2.2.2.2|originsicname=cn\={{ host }},o\=DEVICENAME.domain.com.p7fdbt|sequencenum=1|version=5|administrator=tufinapi|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log Out|operation_number=12|subject=Administrator Login\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}-lm" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Oct  9 11:05:15 DEVICENAME time=1570633513|hostname=DEVICENAME|product=SmartConsole|action=Accept|ifdir=outbound|origin=1.1.1.1|4.4.4.4|sequencenum=1|time=1570633513|version=5|additional_info=Authentication method: Password based application token|administrator=psanadhya|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log In|operation_number=10|subject=Administrator Login|
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_smartconsole(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=SmartConsole|action=Accept|ifdir=outbound|origin=1.1.1.1|4.4.4.4|sequencenum=1|time={{ epoch }}|version=5|additional_info=Authentication method: Password based application token|administrator=psanadhya|client_ip=3.3.3.3|machine=DEVICENAME|operation=Log In|operation_number=10|subject=Administrator Login|\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <6>kernel: sd 2:0:0:0: SCSI error: return code = 0x00040000
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_os(record_property, setup_splunk, setup_sc4s, get_pid):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"
    pid = get_pid

    mt = env.from_string(
        "{{ mark }}kernel: sd 2:0:0:0: SCSI error: return code = 0x{{pid}}\n"
    )
    message = mt.render(mark="<6>", pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search earliest=-1m@m latest=+1m@m index=osnix "0x{{ pid }}"'
    )
    search = st.render(host=host, pid=pid)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1586182935|hostname=xxxx-xxxx|product=Syslog|ifdir=inbound|loguid={0x0,0x0,0x0,0x0}|origin=10.0.0.164|sequencenum=3|time=1586182935|version=5|default_device_message=<134>ctasd[5665]: Save SenderId lists finished |facility=local use 0|
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_os_nested(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Syslog|ifdir=inbound|loguid={{ host }}{0x0,0x0,0x0,0x3}|origin=10.0.0.0|sequencenum=3|version=5|default_device_message=<134>ctasd[5665]: Save SenderId lists finished |facility=local use 0|\n"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test endpoint source event
# time=1586182935|hostname=abc|product=Endpoint Management|action=Drop|ifdir=inbound|loguid={0x60069850,0x0,0xe03ea00a,0x23654691}|origin=10.160.62.224|originsicname=cn\=cp_mgmt,o\=gw-8be69c..ba5xxz|sequencenum=2|version=5|audit_status=Success|endpointname=C7553927437.WORKGROUP|endpointuser=Administrator@C7553927437|operation=Access Key For Encryptor|subject=Endpoint Activity|uid=2E5FD596-BAEF-4453-BFB0-85598CD43DF6
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_endpoint_management(
    record_property, setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Endpoint Management|action=Drop|ifdir=inbound|loguid={0x60069850,0x0,0xe03ea00a,0x23654691}|origin=10.160.62.224|originsicname=cn\=cp_mgmt,o\=gw-8be69c..ba5xxz|sequencenum=2|version=5|audit_status=Success|endpointname=C7553927437.WORKGROUP|endpointuser=Administrator@C7553927437|operation=Access Key For Encryptor|subject=Endpoint Activity|uid=2E5FD596-BAEF-4453-BFB0-85598CD43DF6"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:endpoint"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test network source event
# time=1586182935|hostname=abc|severity=Medium|product=iOS Profiles|ifdir=inbound|loguid={0x6012bc4c,0x15b,0xd10617ac,0x21e842d}|origin=10.1.46.86|sequencenum=164|time={{ epoch }}|version=5|calc_geo_location=calc_geo_location0|client_name=SandBlast Mobile Protect|client_version=2.71.0.3799|dashboard_orig=dashboard_orig0|device_identification=4839|email_address=email_address16|hardware_model=iPhone / iPhone 6S|host_type=Mobile|incident_time=2018-06-03T22:13:11Z|jailbreak_message=False|mdm_id=DEBD25BA-4609-4E81-BC33-3F8C5683F3DF|os_name=IPhone|os_version=11.2.6|phone_number=phone_number0|protection_type=Active proxy|src_user_name=Marsha Hoskins|status=Installed
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_ios_profile(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|severity=Medium|product=iOS Profiles|ifdir=inbound|loguid={0x6012bc4c,0x15b,0xd10617ac,0x21e842d}|origin=10.1.46.86|sequencenum=164|time={{ epoch }}|version=5|calc_geo_location=calc_geo_location0|client_name=SandBlast Mobile Protect|client_version=2.71.0.3799|dashboard_orig=dashboard_orig0|device_identification=4839|email_address=email_address16|hardware_model=iPhone / iPhone 6S|host_type=Mobile|incident_time=2018-06-03T22:13:11Z|jailbreak_message=False|mdm_id=DEBD25BA-4609-4E81-BC33-3F8C5683F3DF|os_name=IPhone|os_version=11.2.6|phone_number=phone_number0|protection_type=Active proxy|src_user_name=Marsha Hoskins|status=Installed"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:network"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test audit source event
# time=1586182935|hostname=abc|product=SmartUpdate|action=Accept|ifdir=outbound|loguid={0x6023d54c,0x0,0x6563a00a,0x3431e7e4}|origin=10.160.99.101|originsicname=cn\=cp_mgmt,o\=gw-02bd87..4zrt7d|sequencenum=6|time={{ epoch }}|version=5|additional_info=Performed 'Attach License' on 10.160.99.101|administrator=admin|client_ip=10.160.99.102|machine=C1359997769|operation=Modify Object|operation_number=1|subject=Object Manipulation
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_smartupdate(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=SmartUpdate|action=Accept|ifdir=outbound|loguid={0x6023d54c,0x0,0x6563a00a,0x3431e7e4}|origin=10.160.99.101|originsicname=cn\=cp_mgmt,o\=gw-02bd87..4zrt7d|sequencenum=6|time={{ epoch }}|version=5|additional_info=Performed 'Attach License' on 10.160.99.101|administrator=admin|client_ip=10.160.99.102|machine=C1359997769|operation=Modify Object|operation_number=1|subject=Object Manipulation"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1611044939|hostname=gw-8be69c|severity=Low|product=Endpoint Compliance|ifdir=inbound|loguid={0x60069d03,0x0,0xe03ea00a,0x23654691}|origin=10.160.62.224|sequencenum=1|version=1|action_comment= |client_name=Check Point Endpoint Security Client|client_version=84.30.6614|description= |event_type=Policy Update|host_type=Desktop|installed_products=Media Encryption & Port Protection; Compliance; Anti-Malware; Url Filtering; Anti-Bot; Forensics; Threat Emulation|local_time=1611044939|machine_guid= |os_name=Windows Server 10.0 Standard Server Edition|os_version=10.0-14393-SP0.0-SMP|policy_date=1610103648|policy_guid={5E122911-49AE-40ED-A91B-0B56576E4549}|policy_name=default_compliance_policy|policy_type=60|policy_version=1|product_family=Endpoint|src=10.160.177.73|src_machine_name=C7553927437|src_user_name=Administrator|user_name= |user_sid=S-1-5-21-1704411108-3626445783-306313190-500
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_endpoint_compliance(
    record_property, setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|severity=Low|product=Endpoint Compliance|ifdir=inbound|loguid={0x60069d03,0x0,0xe03ea00a,0x23654691}|origin=10.160.62.224|sequencenum=1|version=1|action_comment= |client_name=Check Point Endpoint Security Client|client_version=84.30.6614|description= |event_type=Policy Update|host_type=Desktop|installed_products=Media Encryption & Port Protection; Compliance; Anti-Malware; Url Filtering; Anti-Bot; Forensics; Threat Emulation|local_time=1611044939|machine_guid= |os_name=Windows Server 10.0 Standard Server Edition|os_version=10.0-14393-SP0.0-SMP|policy_date=1610103648|policy_guid={5E122911-49AE-40ED-A91B-0B56576E4549}|policy_name=default_compliance_policy|policy_type=60|policy_version=1|product_family=Endpoint|src=10.160.177.73|src_machine_name=C7553927437|src_user_name=Administrator|user_name= |user_sid=S-1-5-21-1704411108-3626445783-306313190-500"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:endpoint"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1613022553|hostname=gw-02bd87|product=Mobile Access|ifdir=outbound|loguid={0x6024c55a,0x2,0x6563a00a,0x346ce8b1}|origin=10.160.99.101|originsicname=cn\=cp_mgmt,o\=gw-02bd87..4zrt7d|sequencenum=2|time=1613022553|version=5|message=All gateways successfully notified about the revocation of certificate with serial no. '49681'
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_mobile_access(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Mobile Access|ifdir=outbound|loguid={0x6024c55a,0x2,0x6563a00a,0x346ce8b1}|origin=10.160.99.101|originsicname=cn\=cp_mgmt,o\=gw-02bd87..4zrt7d|sequencenum=2|time={{ epoch }}|version=5|message=All gateways successfully notified about the revocation of certificate with serial no. '49681'"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:network"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1703062311|hostname=gw-313a04|product=Check Point GO Password Reset|action=Accept|ifdir=outbound|loguid={0x6582ab28,0x0,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time=1703062311|version=5|administrator=admin|client_ip=10.160.3.181|machine=C6828388989|operation=Log Out|operation_number=12|subject=Administrator Login
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_check_point_go_password_reset(
    record_property, setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Check Point GO Password Reset|action=Accept|ifdir=outbound|loguid={0x6582ab28,0x0,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time={{ epoch }}|version=5|administrator=admin|client_ip=10.160.3.181|machine=C6828388989|operation=Log Out|operation_number=12|subject=Administrator Login"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1703070563|hostname=gw-313a04|product=Database Tool|action=Accept|ifdir=outbound|loguid={0x6582cb65,0x0,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time=1703070563|version=5|administrator=admin|client_ip=10.160.3.181|machine=C6828388989|operation=Log Out|operation_number=12|subject=Administrator Login
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_database_tool(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Database Tool|action=Accept|ifdir=outbound|loguid={0x6582cb65,0x0,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time={{ epoch }}|version=5|administrator=admin|client_ip=10.160.3.181|machine=C6828388989|operation=Log Out|operation_number=12|subject=Administrator Login"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1703168085|hostname=gw-313a04|product=FG VPN-1 & FireWall-1|layer_name=Network|layer_name=URL_APP|layer_uuid=38271c2f-ab44-4e25-9aa4-e219cb6e12cf|layer_uuid=789a1bbd-8125-4f7a-a420-179ce276e60f|match_id=2|match_id=16777218|parent_rule=0|parent_rule=0|rule_action=Accept|rule_action=Accept|rule_name=Cleanup rule|rule_name=Cleanup rule|rule_uid=2b922948-da96-4c9d-a654-063e0183f9ae|rule_uid=b72f0dee-0224-4f76-b79e-563f1cf3d3ef|action=Accept|conn_direction=External|contextnum=1|ifdir=inbound|ifname=eth0|logid=6|loguid={0x76e2147d,0x528aea2e,0x75e2f4c,0x22ec9c69}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time=1703168085|version=5|__nsons=0|__p_dport=0|__pos=7|bytes=152|client_inbound_bytes=76|client_inbound_interface=eth0|client_inbound_packets=1|client_outbound_bytes=76|client_outbound_packets=2|context_num=1|dst=40.119.6.228|elapsed=0|fg-1_client_in_rule_name=Default|fg-1_client_out_rule_name=Default|fg-1_server_in_rule_name=Default|fg-1_server_out_rule_name=Default|hll_key=6193773038144685443|inzone=External|lastupdatetime=1703168125|nat_addtnl_rulenum=0|nat_rule_uid=89feaaba-a367-4972-bc44-9da7878c59c1|nat_rulenum=1|outzone=External|packets=3|proto=17|s_port=123|segment_time=1703168085|server_inbound_bytes=76|server_inbound_packets=1|server_outbound_bytes=76|server_outbound_packets=2|service=123|service_id=ntp-udp|src=10.160.50.230|start_time=1703168085|xlatedport=0|xlatedst=0.0.0.0|xlatesport=43710|xlatesrc=10.160.142.204
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_fg_vpn_and_firewall(
    record_property, setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=FG VPN-1 & FireWall-1|layer_name=Network|layer_name=URL_APP|layer_uuid=38271c2f-ab44-4e25-9aa4-e219cb6e12cf|layer_uuid=789a1bbd-8125-4f7a-a420-179ce276e60f|match_id=2|match_id=16777218|parent_rule=0|parent_rule=0|rule_action=Accept|rule_action=Accept|rule_name=Cleanup rule|rule_name=Cleanup rule|rule_uid=2b922948-da96-4c9d-a654-063e0183f9ae|rule_uid=b72f0dee-0224-4f76-b79e-563f1cf3d3ef|action=Accept|conn_direction=External|contextnum=1|ifdir=inbound|ifname=eth0|logid=6|loguid={0x76e2147d,0x528aea2e,0x75e2f4c,0x22ec9c69}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time={{ epoch }}|version=5|__nsons=0|__p_dport=0|__pos=7|bytes=152|client_inbound_bytes=76|client_inbound_interface=eth0|client_inbound_packets=1|client_outbound_bytes=76|client_outbound_packets=2|context_num=1|dst=40.119.6.228|elapsed=0|fg-1_client_in_rule_name=Default|fg-1_client_out_rule_name=Default|fg-1_server_in_rule_name=Default|fg-1_server_out_rule_name=Default|hll_key=6193773038144685443|inzone=External|lastupdatetime=1703168125|nat_addtnl_rulenum=0|nat_rule_uid=89feaaba-a367-4972-bc44-9da7878c59c1|nat_rulenum=1|outzone=External|packets=3|proto=17|s_port=123|segment_time=1703168085|server_inbound_bytes=76|server_inbound_packets=1|server_outbound_bytes=76|server_outbound_packets=2|service=123|service_id=ntp-udp|src=10.160.50.230|start_time=1703168085|xlatedport=0|xlatedst=0.0.0.0|xlatesport=43710|xlatesrc=10.160.142.204"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cp_log" source="checkpoint:firewall"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1703168085|hostname=gw-313a04|product=QoS|action=Accept|ifdir=inbound|loguid={0xd5b78c6e,0x5faa26e,0xddf9bd6a,0x657f411d}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=3|time=1703168085|version=5|dst=40.119.6.228|fg-1_client_in_rule_name=Default|fg-1_client_out_rule_name=Default|fg-1_server_in_rule_name=Default|fg-1_server_out_rule_name=Default|lastupdatetime=1703168085|proto=17|s_port=123|service=123|src=10.160.50.230
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_qos(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=QoS|action=Accept|ifdir=inbound|loguid={0xd5b78c6e,0x5faa26e,0xddf9bd6a,0x657f411d}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=3|time={{ epoch }}|version=5|dst=40.119.6.228|fg-1_client_in_rule_name=Default|fg-1_client_out_rule_name=Default|fg-1_server_in_rule_name=Default|fg-1_server_out_rule_name=Default|lastupdatetime=1703168085|proto=17|s_port=123|service=123|src=10.160.50.230"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cp_log" source="checkpoint:firewall"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1703167535|hostname=gw-313a04|product=cpmidu_update_tool|action=Accept|ifdir=outbound|loguid={0x65844630,0x0,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time=1703167535|version=5|administrator=System|client_ip=10.160.142.204|domain_name=SMC User|fieldschanges=IPS version was updated from 635238481 to 635238507|operation=IPS Update|sendtotrackerasadvancedauditlog=0|session_description=IPS|session_name=IPS|session_uid=17954f55-6f8b-4e5c-92d4-fccd7d7361a6|subject=IPS Update
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_cpmidu_update_tool(
    record_property, setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=cpmidu_update_tool|action=Accept|ifdir=outbound|loguid={0x65844630,0x0,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time={{ epoch }}|version=5|administrator=System|client_ip=10.160.142.204|domain_name=SMC User|fieldschanges=IPS version was updated from 635238481 to 635238507|operation=IPS Update|sendtotrackerasadvancedauditlog=0|session_description=IPS|session_name=IPS|session_uid=17954f55-6f8b-4e5c-92d4-fccd7d7361a6|subject=IPS Update"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1702994835|hostname=gw-313a04|product=query-database|action=Accept|ifdir=outbound|loguid={0x658291c8,0x4,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time=1702994835|version=5|administrator=localhost|client_ip=127.0.0.1|machine=gw-313a04|operation=Log Out|operation_number=12|subject=Administrator Login
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_query_database(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=query-database|action=Accept|ifdir=outbound|loguid={0x658291c8,0x4,0xcc8ea00a,0x3fffbd01}|origin=10.160.142.204|originsicname=cn\=cp_mgmt,o\=gw-313a04..fhsx6t|sequencenum=1|time={{ epoch }}|version=5|administrator=localhost|client_ip=127.0.0.1|machine=gw-313a04|operation=Log Out|operation_number=12|subject=Administrator Login"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log" source="checkpoint:audit"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1692614010|hostname=nevis2-backup-mlm|severity=Low|confidence_level=High|product=Anti Phishing|action=Detect|ifdir=inbound|ifname=MTA|loguid={0x8745b56b,0x40b00845,0x924c2a3c,0x150a9782}|origin=194.29.38.29|originsicname=CN\=il-dmz-tls-05.dummydomain.com,O\=natasha..8ye75g|sequencenum=5|time=1692614010|version=5|dst=194.29.38.29|email_subject= The Morning: Flight risk|from=chrisr+caf_\=chrisri\=dummydomain.com@avanan.com|log_id=0|original_queue_id=4RTpjJ6qfGz6mkC|protection_type=SPAM|proto=6|s_port=0|service=25|src=194.29.47.47|to=chrisri@dummydomain.com|triggered_by=MTA
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_anti_phishing(record_property, setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Anti Phishing|action=Detect|ifdir=inbound|ifname=MTA|loguid={0x8745b56b,0x40b00845,0x924c2a3c,0x150a9782}|origin=194.29.38.29|originsicname=CN\=il-dmz-tls-05.dummydomain.com,O\=natasha..8ye75g|sequencenum=5|time={{ epoch }}|version=5|dst=194.29.38.29|email_subject= The Morning: Flight risk|from=chrisr+caf_\=chrisri\=dummydomain.com@avanan.com|log_id=0|original_queue_id=4RTpjJ6qfGz6mkC|protection_type=SPAM|proto=6|s_port=0|service=25|src=194.29.47.47|to=chrisri@dummydomain.com|triggered_by=MTA"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=email host="{{ host }}" sourcetype="cp_log" source="checkpoint:email"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# time=1693202076|hostname=nevis2-backup-mlm|product=Anti-Spam and Email Security|action=Accept|ifdir=inbound|ifname=MTA|loguid={0x64ec369d,0xc4,0xe07fa8c0,0x205ec071}|origin=194.29.38.29|sequencenum=1|time=1693202076|version=5|dst=194.29.38.29|email_control=Content Anti Spam|email_id=1|email_recipients_num=1|email_session_id={64EC3698-0-1D261DC2-2A3D}|email_spam_category=Non Spam|email_subject= Harmony Mobile - Warning Severity Audit Alert|from=bounces+2173712-9999-adonati\=dummydomain.com@sendgrid.net|proto=6|s_port=0|scan_direction=to/from this gateway|service=25|src=194.29.47.47|src_country=ISR|to=adonati@dummydomain.com
@pytest.mark.addons("checkpoint")
def test_checkpoint_splunk_anti_spam_and_email_security(
    record_property, setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        "time={{ epoch }}|hostname={{ host }}|product=Anti-Spam and Email Security|action=Accept|ifdir=inbound|ifname=MTA|loguid={0x64ec369d,0xc4,0xe07fa8c0,0x205ec071}|origin=194.29.38.29|sequencenum=1|time={{ epoch }}|version=5|dst=194.29.38.29|email_control=Content Anti Spam|email_id=1|email_recipients_num=1|email_session_id={64EC3698-0-1D261DC2-2A3D}|email_spam_category=Non Spam|email_subject= Harmony Mobile - Warning Severity Audit Alert|from=bounces+2173712-9999-adonati\=dummydomain.com@sendgrid.net|proto=6|s_port=0|scan_direction=to/from this gateway|service=25|src=194.29.47.47|src_country=ISR|to=adonati@dummydomain.com"
    )
    message = mt.render(mark="<111>", host=host, bsd=bsd, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=email host="{{ host }}" sourcetype="cp_log" source="checkpoint:email"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

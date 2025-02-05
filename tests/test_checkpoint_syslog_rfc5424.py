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

# Test Anti Malware
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 action="Detect" flags="311552" ifdir="outbound" ifname="eth0" loguid="{0xbbf1236f,0xd5d32253,0xc1bcfade,0x3753c3e6}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="1" time="1612779574" version="5" __policy_id_tag="product=VPN-1 & FireWall-1[db_tag={93CEED8D-9ADE-6343-8B89-54FB5A068DC3};mgmt=gw-02bd87;date=1610491680;policy_name=Standard\]" confidence_level="5" dst="91.195.240.13" http_host="update-help.com" lastupdatetime="1612779738" log_id="2" malware_action="Communication with C&C site" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" method="GET" packet_capture_name="src-10.160.59.141.cap" packet_capture_time="1612779677" packet_capture_unique_id="time1612779574.id1c3adad8.blade04" policy="Standard" policy_time="1612776132" product="Anti Malware" protection_id="00591E0A5" protection_name="APT_RampantKitten.TC.ah" protection_type="URL reputation" proto="6" proxy_src_ip="10.160.59.141" received_bytes="44245" resource="http://update-help.com/" s_port="54470" scope="10.160.59.141" sent_bytes="2624" service="80" session_id="{0x60211036,0x0,0xb3d6e900,0xc68052fb}" severity="4" smartdefense_profile="Optimized" src="10.160.59.141" suppressed_logs="6" layer_name="Standard Threat Prevention" layer_uuid="{75CC4D40-8C8C-4CD6-AF25-51063A9D2AD1}" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" smartdefense_profile="Optimized" user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36" vendor_list="Check Point ThreatCloud" web_client_type="Chrome"]
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_anti_malware(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 action="Detect" flags="311552" ifdir="outbound" ifname="eth0" loguid="{0xbbf1236f,0xd5d32253,0xc1bcfade,0x3753c3e6}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="1" time="{{ epoch }}" version="5" __policy_id_tag="product=VPN-1 & FireWall-1[db_tag={93CEED8D-9ADE-6343-8B89-54FB5A068DC3};mgmt=gw-02bd87;date=1610491680;policy_name=Standard\]" confidence_level="5" dst="91.195.240.13" http_host="update-help.com" lastupdatetime="1612779738" log_id="2" malware_action="Communication with C&C site" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" method="GET" packet_capture_name="src-10.160.59.141.cap" packet_capture_time="1612779677" packet_capture_unique_id="time1612779574.id1c3adad8.blade04" policy="Standard" policy_time="1612776132" product="Anti Malware" protection_id="00591E0A5" protection_name="APT_RampantKitten.TC.ah" protection_type="URL reputation" proto="6" proxy_src_ip="10.160.59.141" received_bytes="44245" resource="http://update-help.com/" s_port="54470" scope="10.160.59.141" sent_bytes="2624" service="80" session_id="{0x60211036,0x0,0xb3d6e900,0xc68052fb}" severity="4" smartdefense_profile="Optimized" src="10.160.59.141" suppressed_logs="6" layer_name="Standard Threat Prevention" layer_uuid="{75CC4D40-8C8C-4CD6-AF25-51063A9D2AD1}" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" smartdefense_profile="Optimized" user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36" vendor_list="Check Point ThreatCloud" web_client_type="Chrome"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:ids_malware"'
    )
    search = st.render(epoch=epoch, bsd=bsd, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test Threat Emulation
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 action="Accept" flags="280832" ifdir="inbound" ifname="eth0" loguid="{0x4b397cf0,0x530e24fb,0x1b71ea26,0x27225237}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="5" time="1612815085" version="5" __policy_id_tag="product=VPN-1 & FireWall-1[db_tag={93CEED8D-9ADE-6343-8B89-54FB5A068DC3};mgmt=gw-02bd87;date=1610491680;policy_name=Standard\]" analyzed_on="Check Point Threat Cloud" confidence_level="0" content_length="456201" content_type="application/octet-stream" dst="173.194.184.234" emulated_on="Win7 64b,Office 2010,Adobe 11" http_host="r5---sn-p5qlsndd.gvt1.com" http_server="downloads" http_status="206" lastupdatetime="1612815085" log_id="4000" log_uid="{3C6AD7C2-72C9-6146-BDD0-BC61D8C2720D}" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" method="GET" policy="Standard" policy_time="1612783608" product="Threat Emulation" protection_type="HTTPEmulation" proto="6" protocol="HTTP" proxy_src_ip="10.160.59.141" resource="dummy_resource" s_port="54750" scope="10.160.59.141" service="80" session_id="{0x3c6ad7c2,0x72c96146,0xbdd0bc61,0xd8c2720d}" severity="0" sig_id="0" smartdefense_profile="Optimized" src="10.160.59.141" te_verdict_determined_by="Win7 64b,Office 2010,Adobe 11: trusted source. " layer_name="Standard Threat Prevention" layer_uuid="{75CC4D40-8C8C-4CD6-AF25-51063A9D2AD1}" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" smartdefense_profile="Optimized" user_agent="Microsoft BITS/7.8" verdict="Benign" web_client_type="Other: Microsoft BITS\/7.8"]

@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_threat_emulation(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 action="Accept" flags="280832" ifdir="inbound" ifname="eth0" loguid="{0x4b397cf0,0x530e24fb,0x1b71ea26,0x27225237}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="5" time="{{ epoch }}" version="5" __policy_id_tag="product=VPN-1 & FireWall-1[db_tag={93CEED8D-9ADE-6343-8B89-54FB5A068DC3};mgmt=gw-02bd87;date=1610491680;policy_name=Standard\]" analyzed_on="Check Point Threat Cloud" confidence_level="0" content_length="456201" content_type="application/octet-stream" dst="173.194.184.234" emulated_on="Win7 64b,Office 2010,Adobe 11" http_host="r5---sn-p5qlsndd.gvt1.com" http_server="downloads" http_status="206" lastupdatetime="1612815085" log_id="4000" log_uid="{3C6AD7C2-72C9-6146-BDD0-BC61D8C2720D}" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" method="GET" policy="Standard" policy_time="1612783608" product="Threat Emulation" protection_type="HTTPEmulation" proto="6" protocol="HTTP" proxy_src_ip="10.160.59.141" resource="dummy_resource" s_port="54750" scope="10.160.59.141" service="80" session_id="{0x3c6ad7c2,0x72c96146,0xbdd0bc61,0xd8c2720d}" severity="0" sig_id="0" smartdefense_profile="Optimized" src="10.160.59.141" te_verdict_determined_by="Win7 64b,Office 2010,Adobe 11: trusted source. " layer_name="Standard Threat Prevention" layer_uuid="{75CC4D40-8C8C-4CD6-AF25-51063A9D2AD1}" malware_rule_id="{A2B8ED86-C9D0-4B0E-9334-C3CFA223CFC2}" smartdefense_profile="Optimized" user_agent="Microsoft BITS/7.8" verdict="Benign" web_client_type="Other: Microsoft BITS\/7.8"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:ids_malware"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test URL Filtering
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 flags="166216" ifdir="outbound" loguid="{0x6021fc5b,0x1,0x6563a00a,0x335f665b}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="2" time="1612840025" version="5" db_ver="21020901" description="Gateway was updated with database version: 3022101." product="URL Filtering" severity="1" update_status="updated"]
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_url_filtering(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 flags="166216" ifdir="outbound" loguid="{0x6021fc5b,0x1,0x6563a00a,0x335f665b}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="2" time="{{ epoch }}" version="5" db_ver="21020901" description="Gateway was updated with database version: 3022101." product="URL Filtering" severity="1" update_status="updated"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:web"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test VPN-1 & FireWall-1
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 action="Accept" flags="810244" ifdir="inbound" ifname="eth0" logid="0" loguid="{0x4d4d455b,0x35b8a7f2,0xdf15314d,0x5765225e}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="74" time="1612518129" version="5" __policy_id_tag="product=VPN-1 & FireWall-1[db_tag={93CEED8D-9ADE-6343-8B89-54FB5A068DC3};mgmt=gw-02bd87;date=1610491680;policy_name=Standard\]" dst="10.160.99.101" hll_key="9901336306766781296" inzone="Internal" layer_name="Network" layer_name="Web" layer_uuid="f5cec687-05e5-4573-b1dc-08119f24cbc9" layer_uuid="d9050599-e213-4537-b7b5-3d203031a58f" match_id="1" match_id="16777217" parent_rule="0" parent_rule="0" rule_action="Accept" rule_action="Accept" rule_name="Cleanup rule" rule_uid="d7a2b9f5-9c83-4ea4-b22d-a07db9d24490" rule_uid="c8c796c4-64ce-4c4d-a9db-0534737f89d9" outzone="Local" product="VPN-1 & FireWall-1" proto="17" s_port="443" service="26796" src="8.8.8.8"]
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_vpn_and_firewall(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 action="Accept" flags="810244" ifdir="inbound" ifname="eth0" logid="0" loguid="{0x4d4d455b,0x35b8a7f2,0xdf15314d,0x5765225e}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="74" time="{{ epoch }}" version="5" __policy_id_tag="product=VPN-1 & FireWall-1[db_tag={93CEED8D-9ADE-6343-8B89-54FB5A068DC3};mgmt=gw-02bd87;date=1610491680;policy_name=Standard\]" dst="10.160.99.101" hll_key="9901336306766781296" inzone="Internal" layer_name="Network" layer_name="Web" layer_uuid="f5cec687-05e5-4573-b1dc-08119f24cbc9" layer_uuid="d9050599-e213-4537-b7b5-3d203031a58f" match_id="1" match_id="16777217" parent_rule="0" parent_rule="0" rule_action="Accept" rule_action="Accept" rule_name="Cleanup rule" rule_uid="d7a2b9f5-9c83-4ea4-b22d-a07db9d24490" rule_uid="c8c796c4-64ce-4c4d-a9db-0534737f89d9" outzone="Local" product="VPN-1 & FireWall-1" proto="17" s_port="443" service="26796" src="8.8.8.8"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:firewall"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test WEB_API_INTERNAL
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 action="Accept" flags="163872" ifdir="outbound" loguid="{0x60251375,0x0,0x6563a00a,0x34bbe8bb}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="1" time="1613042548" version="5" additional_info="Authentication method: Password based application token" administrator="admin" client_ip="10.160.99.102" machine="10.160.99.102" operation="Log In" operation_number="10" product="WEB_API_INTERNAL" subject="Administrator Login"]
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_web_api_internal(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 action="Accept" flags="163872" ifdir="outbound" loguid="{0x60251375,0x0,0x6563a00a,0x34bbe8bb}" origin="10.160.99.101" originsicname="cn={{ host }},o=gw-02bd87..4zrt7d" sequencenum="1" time="{{ epoch }}" version="5" additional_info="Authentication method: Password based application token" administrator="admin" client_ip="10.160.99.102" machine="10.160.99.102" operation="Log In" operation_number="10" product="WEB_API_INTERNAL" subject="Administrator Login"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:audit" product="WEB_API_INTERNAL"'
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
def test_checkpoint_syslog_cli(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 flags="131104" ifdir="inbound" loguid="{0x62176424,0x15,0xb00a00a,0x3fffb255}" origin="10.160.0.11" sequencenum="6" time="{{ epoch }}" version="5" administrator="admin" fieldschanges="NTP secondary server is set to ntp2.checkpoint.com " machine="gw-019d98" objectname="NTP" operation="Set Object" product="CLI" subject="Object Manipulation"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:audit" product="CLI"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test iOS Profiles
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 flags="131072" ifdir="inbound" loguid="{0x60215107,0x169a,0xd10617ac,0x4468886}" origin="10.1.46.86" sequencenum="4138" time="1612795822" version="5" calc_geo_location="calc_geo_location0" client_name="SandBlast Mobile Protect" client_version="2.72.8.3943" dashboard_orig="dashboard_orig0" device_identification="4624" email_address="email_address44" hardware_model="iPhone / iPhone 8" host_type="Mobile" incident_time="2018-06-03T17:33:09Z" jailbreak_message="False" mdm_id="E726405B-4BCF-46C6-8D1B-6F1A71E67D5D" os_name="IPhone" os_version="11.3.1" phone_number="phone_number24" product="iOS Profiles" protection_type="Global proxy" severity="0" src_user_name="Mike Johnson1" status="Removed"]
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_ios_profiles(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 flags="131072" ifdir="inbound" loguid="{0x60215102,0x269a,0xd20617ac,0x2468886}" origin="10.1.46.86" sequencenum="4138" time="{{ epoch }}" version="5" calc_geo_location="calc_geo_location0" client_name="SandBlast Mobile Protect" client_version="2.72.8.3943" dashboard_orig="dashboard_orig0" device_identification="4624" email_address="email_address44" hardware_model="iPhone / iPhone 8" host_type="Mobile" incident_time="2018-06-03T17:33:09Z" jailbreak_message="False" mdm_id="E726405B-4BCF-46C6-8D1B-6F1A71E67D5D" os_name="IPhone" os_version="11.3.1" phone_number="phone_number24" product="iOS Profiles" protection_type="Global proxy" severity="0" src_user_name="Mike Johnson1" status="Removed"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:network"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# Test Endpoint Compliance
# <134>1 2021-02-08T10:19:34Z gw-02bd87 CheckPoint 26203 - [sc4s@2620 flags="131072" ifdir="inbound" loguid="{0x60215107,0x169a,0xd10617ac,0x4468886}" origin="10.1.46.86" sequencenum="4138" time="1612795822" version="5" calc_geo_location="calc_geo_location0" client_name="SandBlast Mobile Protect" client_version="2.72.8.3943" dashboard_orig="dashboard_orig0" device_identification="4624" email_address="email_address44" hardware_model="iPhone / iPhone 8" host_type="Mobile" incident_time="2018-06-03T17:33:09Z" jailbreak_message="False" mdm_id="E726405B-4BCF-46C6-8D1B-6F1A71E67D5D" os_name="IPhone" os_version="11.3.1" phone_number="phone_number24" product="Endpoint Compliance" protection_type="Global proxy" severity="0" src_user_name="Mike Johnson1" status="Removed"]
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_endpoint_compliance(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 flags="131072" ifdir="inbound" loguid="{0x60215107,0x169a,0xd10617ac,0x4468886}" origin="10.1.46.86" sequencenum="4138" time="{{ epoch }}" version="5" calc_geo_location="calc_geo_location0" client_name="SandBlast Mobile Protect" client_version="2.72.8.3943" dashboard_orig="dashboard_orig0" device_identification="4624" email_address="email_address44" hardware_model="iPhone / iPhone 8" host_type="Mobile" incident_time="2018-06-03T17:33:09Z" jailbreak_message="False" mdm_id="E726405B-4BCF-46C6-8D1B-6F1A71E67D5D" os_name="IPhone" os_version="11.3.1" phone_number="phone_number24" product="Endpoint Compliance" protection_type="Global proxy" severity="0" src_user_name="Mike Johnson1" status="Removed"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:endpoint" product="Endpoint Compliance"'
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
def test_checkpoint_syslog_endpoint(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 action="Accept" flags="163872" ifdir="outbound" loguid="{0x62176424,0x31,0xb00a00a,0x3fffb255}" origin="10.160.0.11" sequencenum="16" time="{{ epoch }}" version="5" administrator="endpoint" advanced_changes=" " client_ip="10.160.0.11" fieldschanges="PolicyUid: Changed from \'{2CA690F1-D473-40D9-914C-0209EA794CB3}\' to \'{cf674316-c2b2-4855-b280-071006d73dd3}\' " logic_changes="PolicyUid: Changed from \'{2CA690F1-D473-40D9-914C-0209EA794CB3}\' to \'{cf674316-c2b2-4855-b280-071006d73dd3}\' " objectname="last_update_for_default_compliance_policy" objecttype="PolicyUpdateTime" operation="Modify Object" product="endpoint" sendtotrackerasadvancedauditlog="0" session_uid="b5c8b6cc-48b2-4592-99a6-71d8f8a68757" subject="Object Manipulation" uid="68e1cf86-ce78-4633-b5d2-1443ab5e2e4e"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:endpoint" product="endpoint"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# Test Identity Awareness 
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_identity_awareness(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 alert="alert" flags="141568" ifdir="inbound" logid="131842" loguid="{0x6217617d,0x8,0xb00a00a,0x3fffdb83}" origin="10.160.0.11" originsicname="cn={{ host }},o=gw-3c215b..jva698" sequencenum="6" time="{{ epoch }}" version="5" error_description="Identity information will be deleted" information="Inbound connection from PDP 127.0.0.1 to this PEP gateway on port 15105 was terminated." product="Identity Awareness"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:sessions" product="Identity Awareness"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# Test Mobile Access
# <134>1 2021-02-08T14:50:06Z r81-t279-leui-main-take-2 CheckPoint 2182 - [sc4s@2620 flags="131072" ifdir="inbound" loguid="{0x60215106,0xb,0xd10617ac,0x4468886}" origin="10.2.46.86" sequencenum="12" time="1612795806" version="5" app_repackaged="False" app_sig_id="3343cf41cb8736ad452453276b4f7c806ab83143eca0b3ad1e1bc6045e37f6a9" app_version="3.1.15" appi_name="iPGMail" calc_geo_location="calc_geo_location0" client_name="SandBlast Mobile Protect" client_version="2.73.0.3968" dashboard_orig="dashboard_orig0" device_identification="4768" email_address="email_address0" hardware_model="iPhone / iPhone 5S" host_type="Mobile" incident_time="2018-06-04T00:03:41Z" jailbreak_message="False" mdm_id="F2FCB053-5C28-4917-9FED-4821349B86A5" os_name="IPhone" os_version="11.4" phone_number="phone_number0" product="Mobile Access" protection_type="Backup Tool" severity="0" src_user_name="Allen Newsom" status="Installed"
@pytest.mark.addons("checkpoint")
def test_checkpoint_syslog_mobile_access(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} CheckPoint 26203 - [sc4s@2620 flags="131072" ifdir="inbound" loguid="{0x60215106,0xb,0xd10617ac,0x4468886}" origin="10.2.46.86" sequencenum="12" time="{{ epoch }}" version="5" app_repackaged="False" app_sig_id="3343cf41cb8736ad452453276b4f7c806ab83143eca0b3ad1e1bc6045e37f6a9" app_version="3.1.15" appi_name="iPGMail" calc_geo_location="calc_geo_location0" client_name="SandBlast Mobile Protect" client_version="2.73.0.3968" dashboard_orig="dashboard_orig0" device_identification="4768" email_address="email_address0" hardware_model="iPhone / iPhone 5S" host_type="Mobile" incident_time="2018-06-04T00:03:41Z" jailbreak_message="False" mdm_id="F2FCB053-5C28-4917-9FED-4821349B86A5" os_name="IPhone" os_version="11.4" phone_number="phone_number0" product="Mobile Access" protection_type="Backup Tool" severity="0" src_user_name="Allen Newsom" status="Installed"]'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cp_log:syslog" source="checkpoint:network"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

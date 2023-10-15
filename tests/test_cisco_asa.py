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


# Apr 15 2017 00:21:14 192.168.12.1 : %ASA-5-111010: User 'john', running 'CLI' from IP 0.0.0.0, executed 'dir disk0:/dap.xml'
# Apr 15 2017 00:22:27 192.168.12.1 : %ASA-4-313005: No matching connection for ICMP error message: icmp src outside:81.24.28.226 dst inside:72.142.17.10 (type 3, code 0) on outside interface. Original IP payload: udp src 72.142.17.10/40998 dst 194.153.237.66/53.
# Apr 15 2017 00:22:42 192.168.12.1 : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
@pytest.mark.addons("cisco")
def test_cisco_asa_traditional(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n"
    )
    message = mt.render(mark="<127>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:asa" "%ASA-3-003164"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("cisco")
def test_cisco_asa_no_host_no_seq(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}:{{ bsd }} UTC: %ASA-6-302015: Built outbound UDP connection 2234066391 for outside:10.110.192.80/55173 (10.110.192.80/55173)(LOCAL\\xxxxx) to inside:10.96.105.18/53 (10.96.105.18/53) {{ host }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw "{{ host }}" sourcetype="cisco:asa" "%ASA-6-302015"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <164>Jan 31 2020 17:24:03: %ASA-4-402119: IPSEC: Received an ESP packet (SPI= 0x0C190BF9, sequence number= 0x598243) from 192.0.0.1 (user= 192.0.0.1) to 192.0.0.2 that failed anti-replay checking.
@pytest.mark.addons("cisco")
def test_cisco_asa_traditional_nohost(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }}: %ASA-4-402119: IPSEC: Received an ESP packet (SPI= 0x0C190BF9, sequence number= 0x598243) from {{host}} (user= 192.0.0.1) to 192.0.0.2 that failed anti-replay checking.\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw sourcetype="cisco:asa" "%ASA-4-402119" "{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <166>2018-06-27T12:17:46Z asa : %ASA-3-710003: TCP access denied by ACL from 179.236.133.160/8949 to outside:72.142.18.38/23
@pytest.mark.addons("cisco")
def test_cisco_asa_rfc5424(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{ host }} : %ASA-3-005424: TCP access denied by ACL from 179.236.133.160/5424 to outside:72.142.18.38/23 epoch={{ epoch }}\n"
    )
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:asa" "%ASA-3-005424"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <118>2020-02-04T11:00:54Z %FTD-6-430003: DeviceUUID: 90e14378-2081-11e8-a7fa-d34972ba379f, AccessControlRuleAction: Allow, SrcIP: 75.150.94.75, DstIP: 172.30.0.2, SrcPort: 59698, DstPort: 8027, Protocol: tcp, IngressInterface: Outside2, EgressInterface: DMZ, IngressZone: Outside, EgressZone: DMZ, ACPolicy: Rapid7 5525X, AccessControlRuleName: Allow MDM - Out to DMZ, Prefilter Policy: Default Prefilter Policy, User: No Authentication Required, ConnectionDuration: 600, InitiatorPackets: 0, ResponderPackets: 0, InitiatorBytes: 31, ResponderBytes: 0, NAPPolicy: Balanced Security and Connectivity
@pytest.mark.addons("cisco")
def test_cisco_ftd(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}{{ iso }}Z {{ host }} : %FTD-6-430003: DeviceUUID: 90e14378-2081-11e8-a7fa-d34972ba379f, AccessControlRuleAction: Allow, SrcIP: 75.150.94.75, DstIP: 172.30.0.2, SrcPort: 59698, DstPort: 8027, Protocol: tcp, IngressInterface: Outside2, EgressInterface: DMZ, IngressZone: Outside, EgressZone: DMZ, ACPolicy: Rapid7 5525X, AccessControlRuleName: Allow MDM - Out to DMZ, Prefilter Policy: Default Prefilter Policy, User: No Authentication Required, ConnectionDuration: 600, InitiatorPackets: 0, ResponderPackets: 0, InitiatorBytes: 31, ResponderBytes: 0, NAPPolicy: Balanced Security and Connectivity\n"
    )
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:ftd"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("cisco")
def test_cisco_ftd_nopri(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ iso }}Z {{ host }}  %FTD-6-430003: DeviceUUID: 90e14378-2081-11e8-a7fa-d34972ba379f, AccessControlRuleAction: Allow, SrcIP: 75.150.94.75, DstIP: 172.30.0.2, SrcPort: 59698, DstPort: 8027, Protocol: tcp, IngressInterface: Outside2, EgressInterface: DMZ, IngressZone: Outside, EgressZone: DMZ, ACPolicy: Rapid7 5525X, AccessControlRuleName: Allow MDM - Out to DMZ, Prefilter Policy: Default Prefilter Policy, User: No Authentication Required, ConnectionDuration: 600, InitiatorPackets: 0, ResponderPackets: 0, InitiatorBytes: 31, ResponderBytes: 0, NAPPolicy: Balanced Security and Connectivity\n"
    )
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:ftd"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

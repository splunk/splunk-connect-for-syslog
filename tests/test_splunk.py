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

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <1>1 - - SPLUNK - COOKED [fields@274489 t="1627772621.099" h="so1" i="_internal" st="splunkd" s="/opt/splunk/var/log/splunk/metrics.log"] ~~~SM~~~timestartpos::0 timeendpos::29 _subsecond::.099 date_second::41 date_hour::23 date_minute::3 date_year::2021 date_month::july date_mday::31 date_wday::saturday date_zone::0 group::mpool max_used_interval::0 max_used::0 avg_rsv::0 capacity::134217728 used::0 rep_used::0 metric_name::spl.mlog.mpool~~~EM~~~07-31-2021 23:03:41.099 +0000 INFO  Metrics - group=mpool, max_used_interval=0, max_used=0, avg_rsv=0, capacity=134217728, used=0, rep_used=0
def test_splunk_diode_event(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} - - SPLUNK - COOKED [fields@274489 t="{{ epoch }}" h="{{ host }}" i="_internal" st="splunkd" s="/opt/splunk/var/log/splunk/metrics.log"] ~~~SM~~~timestartpos::0 timeendpos::29 _subsecond::.099 date_second::41 date_hour::23 date_minute::3 date_year::2021 date_month::july date_mday::31 date_wday::saturday date_zone::0 group::mpool max_used_interval::0 max_used::0 avg_rsv::0 capacity::134217728 used::0 rep_used::0 metric_name::spl.mlog.mpool~~~EM~~~07-31-2021 23:03:41.099 +0000 INFO  Metrics - group=mpool, max_used_interval=0, max_used=0, avg_rsv=0, capacity=134217728, used=0, rep_used=0'
        + "\n"
    )
    message = mt.render(mark="<1>1", host=host, epoch=epoch, iso=iso)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=_internal host="{{ host }}" sourcetype="splunkd"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <1>1 - - SPLUNK - COOKED [fields@274489 t="1627772621.099" h="so1" i="_metrics" st="splunk_metrics_log" s="/opt/splunk/var/log/splunk/metrics.log"] ~~~SM~~~timestartpos::0 timeendpos::29 _subsecond::.099 date_second::41 date_hour::23 date_minute::3 date_year::2021 date_month::july date_mday::31 date_wday::saturday date_zone::0 group::mpool max_used_interval::0 max_used::0 avg_rsv::0 capacity::134217728 used::0 rep_used::0 metric_name::spl.mlog.mpool~~~EM~~~07-31-2021 23:03:41.099 +0000 INFO  Metrics - group=mpool, max_used_interval=0, max_used=0, avg_rsv=0, capacity=134217728, used=0, rep_used=0
def test_splunk_diode_metric(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} - - SPLUNK - COOKED [fields@274489 t="{{ epoch }}" h="{{ host }}" i="_metrics" st="splunk_metrics_log" s="/opt/splunk/var/log/splunk/metrics.log"] ~~~SM~~~timestartpos::0 timeendpos::29 _subsecond::.099 date_second::41 date_hour::23 date_minute::3 date_year::2021 date_month::july date_mday::31 date_wday::saturday date_zone::0 group::mpool max_used_interval::0 max_used::0 avg_rsv::0 capacity::134217728 used::0 rep_used::0 metric_name::spl.mlog.mpool~~~EM~~~07-31-2021 23:03:41.099 +0000 INFO  Metrics - group=mpool, max_used_interval=0, max_used=0, avg_rsv=0, capacity=134217728, used=0, rep_used=0'
        + "\n"
    )
    message = mt.render(mark="<1>1", host=host, epoch=epoch, iso=iso)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        "mcatalog values(host) values(sourcetype) where index=_metrics host={{ host }}"
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


def test_splunk_diode_winevent(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        """{{ mark }} - - SPLUNK - COOKED [fields@274489 t="{{ epoch }}" h="{{ host }}" i="oswinsec" st="WinEventLog:Security" s="WinEventLog:Security"]  02/05/2022 12:12:59 AM
LogName=Security
EventCode=4624
EventType=0
ComputerName=ip-0ACA0AE2
SourceName=Microsoft Windows security auditing. winevents
Type=Information
RecordNumber=14462
Keywords=Audit Success
TaskCategory=Logon
OpCode=Info
Message=An account was successfully logged on.

Subject:
	Security ID:		NT AUTHORITY\SYSTEM
	Account Name:		IP-0ACA0AE2$
	Account Domain:		WORKGROUP
	Logon ID:		0x3E7

Logon Information:
	Logon Type:		5
	Restricted Admin Mode:	-
	Virtual Account:		No
	Elevated Token:		Yes

Impersonation Level:		Impersonation

New Logon:
	Security ID:		NT AUTHORITY\SYSTEM
	Account Name:		SYSTEM
	Account Domain:		NT AUTHORITY
	Logon ID:		0x3E7
	Linked Logon ID:		0x0
	Network Account Name:	-
	Network Account Domain:	-
	Logon GUID:		{00000000-0000-0000-0000-000000000000}

Process Information:
	Process ID:		0x2bc
	Process Name:		C:\Windows\System32\services.exe

Network Information:
	Workstation Name:	-
	Source Network Address:	-
	Source Port:		-

Detailed Authentication Information:
	Logon Process:		Advapi  
	Authentication Package:	Negotiate
	Transited Services:	-
	Package Name (NTLM only):	-
	Key Length:		0

This event is generated when a logon session is created. It is generated on the computer that was accessed.

The subject fields indicate the account on the local system which requested the logon. This is most commonly a service such as the Server service, or a local process such as Winlogon.exe or Services.exe.

The logon type field indicates the kind of logon that occurred. The most common types are 2 (interactive) and 3 (network).

The New Logon fields indicate the account for whom the new logon was created, i.e. the account that was logged on.

The network fields indicate where a remote logon request originated. Workstation name is not always available and may be left blank in some cases.

The impersonation level field indicates the extent to which a process in the logon session can impersonate.

The authentication information fields provide detailed information about this specific logon request.
	- Logon GUID is a unique identifier that can be used to correlate this event with a KDC event.
	- Transited services indicate which intermediate services have participated in this logon request.
	- Package name indicates which sub-protocol was used among the NTLM protocols.
	- Key length indicates the length of the generated session key. This will be 0 if no session key was requested."""
    )
    message = mt.render(mark="<1>1", host=host, epoch=epoch, iso=iso)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=oswinsec host="{{ host }}" sourcetype="WinEventLog:Security"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

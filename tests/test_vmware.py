# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz
from time import sleep

from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# vpxd 123 - - Event [3481177] [1-1] [2019-05-23T09:03:36.213922Z] [vim.event.UserLoginSessionEvent] [info] [VSPHERE.LOCAL\svc-vcenter-user] [] [3481177] [User VSPHERE.LOCAL\svc-vcenter-user@192.168.10.10 logged in as pyvmomi Python/2.7.13 (Linux; 4.9.0-7-amd64; x86_64)]
def test_linux_vmware(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso_header }}Z {{ host }} vpxa {{ pid }} - - Event [3481177] [1-1] [{{ iso }}Z] [vim.event.UserLoginSessionEvent] [info] [VSPHERE.LOCAL\svc-vcenter-user] [] [3481177] [User VSPHERE.LOCAL\svc-vcenter-user@192.168.10.10 logged in as pyvmomi Python/2.7.13 (Linux; 4.9.0-7-amd64; x86_64)]\n"
    )
    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} {{ pid }} sourcetype="vmware:esxlog:vpxa"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_linux_vmware_nix(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso_header }}Z {{ host }} sshd {{ pid }} - - - Generic event\n"
    )
    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} {{ pid }} sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <46>1 2019-10-24T21:00:02.403Z {{ host }} NSXV 5996 - [nsxv@6876 comp="nsx-manager" subcomp="manager"] Invoking EventHistoryCollector.readNext on session[52db61bf-9c30-1e1f-5a26-8cd7e6f9f552]52032c51-240a-7c30-cd84-4b4246508dbe, operationID=opId-688ef-9725704
def test_linux_vmware_nsx_ietf(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }}1 {{ iso_header }}Z {{ host }} NSX - SYSTEM [nsx@6876 comp="nsx-manager" errorCode="MP4039" subcomp="manager"] Connection verification failed for broker \'10.160.108.196\'. Marking broker unhealthy.\n'
    )
    message = mt.render(mark="<144>", iso_header=iso_header, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:nsxlog:nsx"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


#
def test_linux_vmware_nsx_fw(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} dfwpktlogs: {{ pid }} INET match PASS domain-c7/1001 IN 60 TCP 10.33.24.50/45926->10.33.24.9/8140 S\n"
    )
    message = mt.render(mark="<144>", bsd=bsd, host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host={{ host }} {{ pid }} sourcetype="vmware:nsxlog:dfwpktlogs"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_linux_vmware_vcenter_ietf(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso_header }}Z {{ host }} vmon 2275 - -  <vsan-dps> Reset fail counters of service\n"
    )
    message = mt.render(mark="<144>", iso_header=iso_header, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:vclog:vmon"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <111>1 2020-06-18T08:44:09.039-05:00 host View - 73 [View@6876 Severity="AUDIT_SUCCESS" Module="Broker" EventType="BROKER_USERLOGGEDIN" UserSID="S-1-5-21-873381292-3070774752-20851"]
def test_linux_vmware_horizon_ietf(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }}1 {{ iso_header }}Z {{ host }} View - 73 [View@6876 Severity="AUDIT_SUCCESS" Module="Broker" EventType="BROKER_USERLOGGEDIN" UserSID="S-1-5-21-873381292-3070774752-20851"]\n'
    )
    message = mt.render(mark="<144>", iso_header=iso_header, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:horizon"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vmware_bsd_nix(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = "testvmw-" + get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} sshd[195529]: something something\n"
    )
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


#
#<14>2022-02-11T11:38:23.749Z host cmmdsTimeMachineDump: 1644579494.944824,527e4880-c1ec-8c0b-646d-7d818784807b,16,472131,5f60e727-3b12-e650-9fe0-b47af135162a,2,{"capacityUsed": 669883700346, "l2CacheUsed": 0, "l1CacheUsed": 0, "writeConsolidationRatio": 10, "avgReadsPerSecond": 1, "avgWritesPerSecond": 11, "avgThroughPutUsed": 185856, "avgReadServiceTime": 0, "avgReadQueueTime": 0, "avgWriteServiceTime": 0, "avgWriteQueueTime": 0, "avgDiskReadsPerSec": 0, "avgDiskWritesPerSec": 0, "avgSSDReadsPerSec": 0, "avgSSDWritesPerSec": 0, "estTimeToFailure": 0, "numDataComponents": 27, "logicalCapacityUsed": 0, "physDiskCapacityUsed": 0, "pendingWrite": 0, "pendingDelete": 0, "dgPendingWrite": 0, "dgPendingDelete": 0, "dgLogicalCapacityUsed": 0, "dgAvgDataDestageBytesSec": 37560838, "dgAvgZeroDestageBytesSec": 0, "dgAvgResyncReadBytesPerSec": 0, "dgAvgTo.
#<14>2022-02-11T11:38:23.749Z host cmmdsTimeMachineDump: talReadBytesPerSec": 911767, "dgAvgRecWriteBytesPerSec": 0, "dgAvgTotalWriteBytesPerSec": 872405, "writeBufferSize": 0, "writeBufferUsage": 17259835392, "pendingUnmap": 0}\q.
def test_linux_vmware_bsd_tmd(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }}{{ iso_header }}Z {{ host }} cmmdsTimeMachineDump: 1644579494.944824,527e4880-c1ec-8c0b-646d-7d818784807b,16,472131,5f60e727-3b12-e650-9fe0-b47af135162a,2,{"capacityUsed": 669883700346, "l2CacheUsed": 0, "l1CacheUsed": 0, "writeConsolidationRatio": 10, "avgReadsPerSecond": 1, "avgWritesPerSecond": 11, "avgThroughPutUsed": 185856, "avgReadServiceTime": 0, "avgReadQueueTime": 0, "avgWriteServiceTime": 0, "avgWriteQueueTime": 0, "avgDiskReadsPerSec": 0, "avgDiskWritesPerSec": 0, "avgSSDReadsPerSec": 0, "avgSSDWritesPerSec": 0, "estTimeToFailure": 0, "numDataComponents": 27, "logicalCapacityUsed": 0, "physDiskCapacityUsed": 0, "pendingWrite": 0, "pendingDelete": 0, "dgPendingWrite": 0, "dgPendingDelete": 0, "dgLogicalCapacityUsed": 0, "dgAvgDataDestageBytesSec": 37560838, "dgAvgZeroDestageBytesSec": 0, "dgAvgResyncReadBytesPerSec": 0, "dgAvgTo.\n'
    )
    message = mt.render(mark="<144>", iso_header=iso_header, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    mt = env.from_string(
        '{{ mark }}{{ iso_header }}Z {{ host }} cmmdsTimeMachineDump: talReadBytesPerSec": 911767, "dgAvgRecWriteBytesPerSec": 0, "dgAvgTotalWriteBytesPerSec": 872405, "writeBufferSize": 0, "writeBufferUsage": 17259835392, "pendingUnmap": 0}\q.'
    )
    message = mt.render(mark="<144>", iso_header=iso_header, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:esxlog:cmmdsTimeMachineDump"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_vmware_bsd_vpscache(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vpxa[195529]: something something\n"
    )
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    sleep(5)

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} sshd[195529]: something something\n"
    )
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux_vmware_badsdata(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}{{ iso_header }}Z {{ host }} Vpxa: verbose vpxa[{{ pid }}] [Originator@6876 sub=VpxaCnxHostd opID=WFU-34799d2d] FetchingUpdatesDone callback, time for waiting responce from HOSTD 2373 ms\n"
    )
    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} {{ pid }} sourcetype="vmware:esxlog:vpxa"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux_vmware_vobd(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}{{ iso_header }}Z {{ host }} vobd:  [vmfsCorrelator] 1742724771908us: [vob.vmfs.sesparse.bloomfilter.disabled] Read IO performance maybe impacted for disk ttqlxapp-adm02-flat.vmdk: Non-empty delta disk being opened"
    )
    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:esxlog:vobd"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux_vmware_usc(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}{{ iso_header }}Z {{ host }} ucs-tool-esxi-inv : WARNING  : Command '/opt/ucs_tool_esxi/ucs_ipmitool read_file ucs_tool_last_config.yaml /opt/ucs_tool_esxi/ucs_tool_inv_read_last_config.yaml' failed with return code: 1"
    )
    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:esxlog:ucs-tool-esxi-inv"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_linux_vmware_usbarb(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(
        random.choice(setup_wordlist), random.choice(setup_wordlist)
    )
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}{{ iso_header }}Z {{ host }} usbarb[2000000]: USBArb: new client A000001D00 created, socket 10 added to poll queue"
    )
    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} sourcetype="vmware:esxlog:usbarb"'
    )
    search = st.render(epoch=epoch, host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_vmware_overlapping_with_another_sdata(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key
    pid = random.randint(1000, 32000)

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)
    
    iso = dt.isoformat()[0:26]
    iso_header = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }}{{ iso_header }}Z {{ host }} Vpxa: verbose vpxa[{{ pid }}] [Originator@6876 sub=vpxLro opID=host@23668][meta sequenceId="231559791"][VpxLRO] -- FINISH lro-1204873\n'
    )

    message = mt.render(
        mark="<144>", iso_header=iso_header, iso=iso, host=host, pid=pid
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host={{ host }} {{ pid }} sourcetype="vmware:esxlog:vpxa"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
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
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("nutanix")
def test_nutanix(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ iso }} NTNX-{{ host }}-CVM audispd[00000]: node=ntnx-{{ host }}-cvm type=SYSCALL msg=audit(1651176975.464:2828209): arch=c000003e syscall=2 success=yes exit=6 a0=7f2955ac932e a1=2 a2=3e8 a3=3 items=1 ppid=29680 pid=4684 auid=1000 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=964698 comm="sshd" exe="/usr/sbin/sshd" subj=system_u:system_r:sshd_t:s0-s0:c0.c1023_jnjnhcdebcbdcbhdbcbjkn4'
    )
    message = mt.render(mark="<134>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops  sourcetype="nutanix:syslog*"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

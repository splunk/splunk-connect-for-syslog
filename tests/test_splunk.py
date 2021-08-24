# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <1>1 - - SPLUNK - COOKED [fields@274489 t="1627772621.099" h="so1" i="_internal" st="splunkd" s="/opt/splunk/var/log/splunk/metrics.log"] ~~~SM~~~timestartpos::0 timeendpos::29 _subsecond::.099 date_second::41 date_hour::23 date_minute::3 date_year::2021 date_month::july date_mday::31 date_wday::saturday date_zone::0 group::mpool max_used_interval::0 max_used::0 avg_rsv::0 capacity::134217728 used::0 rep_used::0 metric_name::spl.mlog.mpool~~~EM~~~07-31-2021 23:03:41.099 +0000 INFO  Metrics - group=mpool, max_used_interval=0, max_used=0, avg_rsv=0, capacity=134217728, used=0, rep_used=0
def test_splunk_diode_event(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


# <1>1 - - SPLUNK - COOKED [fields@274489 t="1627772621.099" h="so1" i="_metrics" st="splunk_metrics_log" s="/opt/splunk/var/log/splunk/metrics.log"] ~~~SM~~~timestartpos::0 timeendpos::29 _subsecond::.099 date_second::41 date_hour::23 date_minute::3 date_year::2021 date_month::july date_mday::31 date_wday::saturday date_zone::0 group::mpool max_used_interval::0 max_used::0 avg_rsv::0 capacity::134217728 used::0 rep_used::0 metric_name::spl.mlog.mpool~~~EM~~~07-31-2021 23:03:41.099 +0000 INFO  Metrics - group=mpool, max_used_interval=0, max_used=0, avg_rsv=0, capacity=134217728, used=0, rep_used=0
def test_splunk_diode_metric(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

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

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment
from pytest import mark

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


def test_defaultroute(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{ mark }} {{ bsd }} {{ host }} test something else\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix host="{{ host }}" sourcetype="nix:syslog" source="program:test"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_defaultroute_port(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{ mark }} {{ bsd }} {{ host }} porttest: something else\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][5514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_fallback(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
         "{{ mark }} {{ bsd }} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:>\n"
    )
    message = mt.render(mark="<11>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="sc4s:fallback"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_metrics(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string(
        'mcatalog values(metric_name) WHERE metric_name="spl.sc4syslog.*" AND ("index"="*" OR "index"="_*") BY metric_name | fields metric_name'
    )
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount != 0

def test_tz_fix_ny(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    # 10 minute offset (reserved for future use)
    #   dt = datetime.datetime.now(pytz.timezone('America/New_York')) - datetime.timedelta(minutes=10)

    dt = datetime.datetime.now(pytz.timezone("America/New_York")) - datetime.timedelta(
        minutes=15
    )
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} tzfny-{{ host }} sshd[123]: Timezone America/New_York\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix host="tzfny-{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_tz_fix_ch(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    # 10 minute offset (reserved for future use)
    #   dt = datetime.datetime.now(pytz.timezone('America/New_York')) - datetime.timedelta(minutes=10)

    dt = datetime.datetime.now(pytz.timezone("America/Chicago")) - datetime.timedelta(
        minutes=15
    )
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} tzfchi-{{ host }} sshd[123]: Timezone America/Chicago\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix host="tzfchi-{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1



def test_check_config_version(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):

    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events:startup:err" "Configuration file format is too old" '
    )
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 0


def test_check_config_version_multiple(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):

    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events:startup:err" "you have multiple @version directives" '
    )
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 0


def test_check_sc4s_version(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events:startup:out" "sc4s version=" NOT "UNKNOWN"'
    )
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 1

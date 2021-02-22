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
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="sc4s:fallback" PROGRAM="test"'
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

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][5008])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="sc4s:porttest"'
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

    mt = env.from_string("{{ mark }} {{ bsd }} testvp-{{ host }} test\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="testvp-{{ host }}" sourcetype="sc4s:fallback"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_metrics(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string(
        'mcatalog values(metric_name) WHERE metric_name="syslogng.*" AND ("index"="*" OR "index"="_*") BY metric_name | fields metric_name'
    )
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount != 0


def test_tz_guess(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n"
    )
    message = mt.render(
        mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:asa" "%ASA-3-003164"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1



def test_tz_fix_ny(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    # 10 minute offset (reserved for future use)
    #   dt = datetime.datetime.now(pytz.timezone('America/New_York')) - datetime.timedelta(minutes=10)

    dt = datetime.datetime.now(pytz.timezone("America/New_York")) - datetime.timedelta(minutes=15)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} tzfny-{{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="tzfny-{{ host }}" sourcetype="cisco:asa"'
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


# This test fails on circle; Cisco ACS single test seems to trigger a utf8 error.
def test_check_utf8(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events" "Input is valid utf8"'
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

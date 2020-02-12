# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

def test_defaultroute(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'local', '%b %d %H:%M:%S' %} {{ host }} test something else\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main host=\"{{ host }}\" sourcetype=\"sc4s:fallback\" PROGRAM=\"test\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_internal(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'local', '%b %d %H:%M:%S' %} {{ host }} sc4sdefault[0]: test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main NOT host=\"{{ host }}\" sourcetype=\"sc4s:events\" | head 1")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_fallback(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'local', '%b %d %H:%M:%S' %} testvp-{{ host }} test\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main host=\"testvp-{{ host }}\" sourcetype=\"sc4s:fallback\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
def test_metrics(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string('mcatalog values(metric_name) WHERE metric_name="syslogng.d_*#0" AND ("index"="*" OR "index"="_*") BY index | fields index')
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 1

def test_tz_guess(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }} {% now 'America/Los_Angeles', '%b %d %H:%M:%S' %} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<111>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netfw host=\"{{ host }}\" sourcetype=\"cisco:asa\" \"%ASA-3-003164\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_tz_fix_hst(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.utcnow() - datetime.timedelta(hours=10, minutes=10)
    mt = env.from_string(
        "{{ mark }} {{ dt }} tzfhst-{{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<111>", host=host, dt=dt.strftime('%b %d %H:%M:%S'))

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netfw host=\"tzfhst-{{ host }}\" sourcetype=\"cisco:asa\"")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

def test_tz_fix_ny(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    tz_NY = pytz.timezone('America/New_York')
    dt = datetime.datetime.now(tz_NY) - datetime.timedelta(minutes=10)
    mt = env.from_string(
        "{{ mark }} {{ dt }} tzfny-{{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n")
    message = mt.render(mark="<111>", host=host, dt=dt.strftime('%b %d %H:%M:%S'))

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netfw host=\"tzfny-{{ host }}\" sourcetype=\"cisco:asa\"")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_check_config_version(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main sourcetype=\"sc4s:events:startup:err\" \"Configuration file format is too old\" ")
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 0

def test_check_config_version_multiple(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main sourcetype=\"sc4s:events:startup:err\" \"you have multiple @version directives\" ")
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 0

def test_check_sc4s_version(record_property, setup_wordlist, setup_splunk, setup_sc4s):

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main sourcetype=\"sc4s:events:startup:out\" \"sc4s version=\" NOT \"UNKNOWN\"")
    search = st.render()

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("resultCount", resultCount)

    assert resultCount == 0

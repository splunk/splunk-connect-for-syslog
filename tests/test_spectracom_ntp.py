# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()
# <184>CEAPAPRDNTP01: [system] Log daemon has been restarted (LOGD)
def test_spectracom(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = "test-specntp-" + get_host_key
    host = host.upper()

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}{{ host }}: [system] Log daemon has been restarted (LOGD)\n"
    )
    message = mt.render(mark="<184>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6002])

    st = env.from_string(
        'search index=netops host="{{ host }}" sourcetype="spectracom:ntp"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<35>PAM-tacplus[12023]: auth failed: 2
def test_spectracom_nix(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host =get_host_key

    mt = env.from_string(
        "{{ mark }}PAM-tacplus[12023]: auth failed: 2 {{ host }}\n"
    )
    message = mt.render(mark="<35>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6002])

    st = env.from_string(
        'search index=osnix "{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render( host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<86>apache2: pam_succeed_if(httpd:auth): requirement "user ingroup root" not met by user "aajramirez"
def test_spectracom_nix2(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host =get_host_key
    
    mt = env.from_string(
        "{{ mark }}apache2: pam_succeed_if(httpd:auth): requirement \"user ingroup root\" not met by user \"{{ host }}\"\n"
    )
    message = mt.render(mark="<86>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][6002])

    st = env.from_string(
        'search index=osnix "{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render( host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

# <23> Feb 27 15:00:00 vpn-001 Juniper: 2013-02-27 15:00:00 - ive - [000.000.000.000] SAMPLE::xxx@xxx.xxx(Users)[] - Session timed out for xxx@xxx.xxx.xxx/Users (session:00000000) due to inactivity (last access at 13:59:31 2013/02/27). Idle session identified during routine system scan.
# <23> Feb 27 15:00:00 vpn-001 Juniper: 2013-02-27 15:00:00 - ive - [000.000.000.000] SAMPLE::xxx@xxx.xxx(Users)[User_Role] - Remote address for user xxx@xxx.xxx/Users changed from 000.000.000.000 to 000.000.000.000. Access denied.
def test_juniper_sslvpn_standard(record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s):
    host = get_host_key

    mt = env.from_string(
        "{{ mark }} {% now 'local', '%b %d %H:%M:%S' %} {{ host }} Juniper: {% now 'local', '%Y-%m-%d %H:%M:%S' %} - ive - [000.000.000.000] SAMPLE::xxx@xxx.xxx(Users)[User_Role] - Remote address for user xxx@xxx.xxx/Users changed from 000.000.000.000 to 000.000.000.000. Access denied.")
    message = mt.render(mark="<23>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netfw host=\"{{ host }}\" sourcetype=\"juniper:sslvpn\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

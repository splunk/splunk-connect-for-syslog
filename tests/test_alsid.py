# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import pytest
from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()


# <134>Feb 18 09:37:41 xxxxxx swlogd: bcmd esm info(5) phy_nlp_enable_set: u=0 p=1 enable:1 phyPresent:YES
testdata = [
    '{{ mark }}{{ bsd }} {{ host }} AlsidForAD[4]: "0" "1" "EXAMPLE_AD_FOREST" "EXAMPLE_AD_DOMAIN" "C-DANG-PRIMGROUPID" "critical" "CN=CN=EXAMPLE_AD_ACCOUNT,OU=EXAMPLE_OU,OU=EXAMPLE_OU,DC=EXAMPLE_AD_FOREST,DC=EXAMPLE_AD_DOMAIN,DC=EXAMPLE_AD_FOREST_FQDN,DC=com,DC=au" "427573" "2" "R-DANG-PRIMGROUPID" "1727453" "AccountCn"="EXAMPLE_AD_ACCOUNT" "PrimaryGroupId"="16611" "GroupCn"="EXAMPLE_AD_GROUP_NAME" "DomainName"="EXAMPLE_AD_DOMAIN" "ObjectType"="User" "ObjectTypePrimaryGroupId"="513"',
]


@pytest.mark.parametrize("event", testdata)
def test_alsid(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<166>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=oswinsec _time={{ epoch }} sourcetype="alsid:syslog" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

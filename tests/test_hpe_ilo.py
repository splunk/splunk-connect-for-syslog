# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

import random
from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <134>1 2022-01-27T19:51:46Z host #ILO4 - - - Browser login: Administrator - 10.0.0.0(host.domain.local)
def test_hpe_ilo_4(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{ host }} #ILO4 - - - Browser login: Administrator - 10.0.0.0(host.domain.local)\n"
    )
    message = mt.render(mark="<165>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="hpe:ilo"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<134>1 2023-04-19T18:57:31Z ilo-10-69-5-33 DenialofService - - - iLO detected 3 unauthorized login attempts.
def test_hpe_ilo_event(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{ host }} DenialofService - - - iLO detected 3 unauthorized login attempts."
    )
    message = mt.render(mark="<165>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="hpe:ilo"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


#<134>1 2023-04-19T18:57:31Z ilo-10-69-5-56 Network: Ethernet 10/25Gb 2-port SFP88 XXXXX-ACHT Adapter Connectivity status changed to OK for adapter in slot 2, port 2 ACTION: If the connection is lost, then check the physical connection from the server to its destination device such as interconnect ,blade, switch etc, including any cables. Refer to the NIC issues flowchart in the Troubleshooting Guide for more information.
def test_hpe_ilo_network_event(
    record_property, setup_wordlist, get_host_key, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{ host }} Network: Ethernet 10/25Gb 2-port SFP88 XXXXX-ACHT Adapter Connectivity status changed to OK for adapter in slot 2, port 2 ACTION: If the connection is lost, then check the physical connection from the server to its destination device such as interconnect ,blade, switch etc, including any cables. Refer to the NIC issues flowchart in the Troubleshooting Guide for more information."
    )
    message = mt.render(mark="<165>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="hpe:ilo"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
    
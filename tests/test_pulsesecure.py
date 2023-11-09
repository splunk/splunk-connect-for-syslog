# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape
from pytest import mark

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


@mark.addons("pulse")
def test_pulse_secure_5424(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, _, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso }} {{ host }} PulseSecure: - - - ive | 2020-09-16 18:10:53 | ADM100 | info | 10.251.0.1 |  | 172.30.0.21 | username | Ace Admin |  |  |  |  |  |  | Admin user 'username' has accepted Pulse EULA\n"
    )
    message = mt.render(mark="<14>", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pulse:connectsecure"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@mark.addons("pulse")
def test_pulse_secure_6587(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, _, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso }} {{ host }} PulseSecure: - - - ive | 2020-09-16 18:10:53 | ADM100 | info | 10.251.0.1 |  | 172.30.0.21 | username | Ace Admin |  |  |  |  |  |  | Admin user 'username' has accepted Pulse EULA"
    )
    message = mt.render(mark="<14>", iso=iso, host=host)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="pulse:connectsecure"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@mark.addons("pulse")
def test_pulse_secure_6587_web(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, _, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }}1 {{ iso }} {{ host }} PulseSecure: - - - ive | 2020-09-16 18:10:53 | ADM100 | info | 10.251.0.1 | WebRequest | 172.30.0.21 | username | Ace Admin |  |  |  |  |  |  | Admin user 'username' has accepted Pulse EULA"
    )
    message = mt.render(mark="<14>", iso=iso, host=host)
    message_len = len(message)
    ietf = f"{message_len} {message}"
    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy host="{{ host }}" sourcetype="pulse:connectsecure:web"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import datetime
import random
import re
import time

from jinja2 import Environment
import pytest

from .timeutils import time_operations
from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from package.etc.pylib.parser_source_cache import ip2int, int2ip

env = Environment()


def send_message(message_template, setup_sc4s, host=None):
    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-7]

    mt = env.from_string(message_template)
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    return epoch


@pytest.mark.name_cache
def test_name_cache(get_host_key, setup_splunk, setup_sc4s):
    """
    Send a log event without a valid host.
    Then send another log event with a valid host to generate name cache entry.
    Then send the first event again. It should be assigned host value from the cache.
    """
    template_no_host = "{{ mark }} {{ bsd }} CEF:0|Trend Micro|Deep Security Manager|0.0.0|600|User Signed In|3|src=10.52.116.160|"
    template_with_host = "{{ mark }} {{ bsd }} {{ host }} CEF:0|Trend Micro|Deep Security Manager|0.0.0|600|User Signed In|3|src=10.52.116.160|"

    _ = send_message(template_no_host, setup_sc4s)
    _ = send_message(template_with_host, setup_sc4s, host=get_host_key)
    time.sleep(1) # time to save the new cache entry
    epoch = send_message(template_no_host, setup_sc4s)

    search = f'search _time="{epoch}" index=* host="{get_host_key}"'

    result_count, _ = splunk_single(setup_splunk, search)
    assert result_count == 1


def generate_random_ipv4():
    random_octet = lambda: format(random.randint(0, 255))
    return ".".join([random_octet() for _ in range(4)])

def generate_random_ipv6():
    def generate_random_hex():
        random_hex = format(random.randint(0, 65535), '04x')
        random_hex = re.sub('^0+', '', random_hex) # leading zeros can be skipped
        return random_hex
    return ":".join([generate_random_hex() for _ in range(8)])

@pytest.mark.name_cache
def test_ipv4_utils():
    ip = generate_random_ipv4()
    assert ip == int2ip(ip2int(ip))

def test_ipv6_utils():
    ip = generate_random_ipv6()
    assert ip == int2ip(ip2int(ip))
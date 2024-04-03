# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from time import sleep
import datetime
import socket

from jinja2 import Environment
import pytest

from .splunkutils import  splunk_single
from .timeutils import time_operations

env = Environment()

def sendsingle_return_ip(message, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)

    tried = 0
    while True:
        try:
            sock.connect(server_address)
            break
        except socket:
            tried += 1
            if tried > 90:
                raise
            sleep(1)

    sock.sendall(str.encode(message))
    source_ip = sock.getsockname()[0]
    sock.close()
    return source_ip


@pytest.mark.reverse_dns
def test_reverse_dns_lookup_failure_assigns_source_IP_to_hostname_field(setup_splunk, setup_sc4s):
    """
    Test verifies that when SC4S_USE_REVERSE_DNS is set to True but the hostname cannot be found, 
    the application correctly assigns the source IP to the hostname field.
    """
    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-7]

    template_no_host = "{{ mark }} {{ bsd }} CEF:0|Trend Micro|Deep Security Manager|0.0.0|600|User Signed In|3|src=10.52.116.160|"
    mt = env.from_string(template_no_host)
    message = mt.render(mark="<111>", bsd=bsd)

    source_ip = sendsingle_return_ip(message, setup_sc4s[0], setup_sc4s[1][514])

    search = f'search _time="{epoch}" index=* host="{source_ip}"'

    result_count, _ = splunk_single(setup_splunk, search)
    assert result_count == 1
# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import pytest
import socket

from package.etc.pylib.parser_fix_dns import FixHostnameResolver, FixFQDNResolver


class LogMessage:
    def __init__(self, data):
        self.data = data

    def get_as_str(self, key, default="", repr="internal"):
        return str(self.data.get(key, default))
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value


def get_ip_address(domain):
    return socket.gethostbyname(domain)

@pytest.mark.addons("reverse-dns")
def test_hostname_resolver_success():
    resolver = FixHostnameResolver()
    source_ip = get_ip_address("google.com")
    log_message = LogMessage({
        "SOURCEIP": source_ip
    })
    assert resolver.parse(log_message) == True
    assert isinstance(log_message["HOST"], str)
    assert "." not in log_message["HOST"], "HOST should be short hostname without a top level domain name"

@pytest.mark.addons("reverse-dns")
def test_fqdn_resolver_success():
    resolver = FixFQDNResolver()
    source_ip = get_ip_address("google.com")
    log_message = LogMessage({
        "SOURCEIP": source_ip
    })
    assert resolver.parse(log_message) == True
    assert isinstance(log_message["HOST"], str)
    assert "." in log_message["HOST"], "HOST should be a FQDN with .domain"

@pytest.mark.addons("reverse-dns")
def test_hostname_resolver_invalid_ip():
    resolver = FixHostnameResolver()
    log_message = LogMessage({
        "SOURCEIP": "invalid_ip"
    })
    assert resolver.parse(log_message) == False
    assert "HOST" not in log_message.data

@pytest.mark.addons("reverse-dns")
def test_fqdn_resolver_invalid_ip():
    resolver = FixFQDNResolver()
    log_message = LogMessage({
        "SOURCEIP": "invalid_ip"
    })
    assert resolver.parse(log_message) == False
    assert "HOST" not in log_message.data

@pytest.mark.addons("reverse-dns")
def test_hostname_resolver_search_failed():
    resolver = FixHostnameResolver()
    log_message = LogMessage({
        "SOURCEIP": "10.0.0.1"
    })
    assert resolver.parse(log_message) == False
    assert "HOST" not in log_message.data

@pytest.mark.addons("reverse-dns")
def test_fqdn_resolver_search_failed():
    resolver = FixFQDNResolver()
    log_message = LogMessage({
        "SOURCEIP": "10.0.0.1"
    })
    assert resolver.parse(log_message) == False
    assert "HOST" not in log_message.data


if __name__ == "__main__":
    pytest.main()
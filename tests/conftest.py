# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import os
import random
import socket
import uuid
from time import sleep

import pytest
import requests
import splunklib.client as client


@pytest.fixture(scope="module")
def setup_wordlist():
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.split(path_to_current_file)[0]
    path_to_file = os.path.join(current_directory, "data/wordlist.txt")

    wordlist = [line.rstrip("\n") for line in open(path_to_file)]
    return wordlist


@pytest.fixture
def get_host_key(setup_wordlist):
    part1 = random.choice(setup_wordlist)
    part2 = random.choice(setup_wordlist)
    host = "{}-{}".format(part1, part2)

    return host


def pytest_addoption(parser):
    group = parser.getgroup("splunk-addon-sc4s")

    group.addoption(
        "--sc4s-host",
        action="store",
        dest="sc4s_host",
        default="127.0.0.1",
        help="Address of the sc4s Server",
    )

@pytest.fixture(scope="session")
def sc4s(request, splunk):
    if request.config.getoption("splunk_type") == "external":
        request.fixturenames.append("sc4s_external")
        sc4s = request.getfixturevalue("sc4s_external")
    elif request.config.getoption("splunk_type") == "docker":
        request.fixturenames.append("sc4s_docker")
        sc4s = request.getfixturevalue("sc4s_docker")
    else:
        raise Exception

    yield sc4s


@pytest.fixture(scope="session")
def sc4s_docker(docker_services):
    docker_services.start("sc4s")

    ports = {514: docker_services.port_for("sc4s", 514)}
    for x in range(5000, 5007):
        ports.update({x: docker_services.port_for("sc4s", x)})

    return docker_services.docker_ip, ports


@pytest.fixture(scope="session")
def sc4s_external(request):
    ports = {514: 514}
    for x in range(5000, 5050):
        ports.update({x: x})

    return request.config.getoption("sc4s_host"), ports


@pytest.fixture()
def setup_sc4s(sc4s):
    return sc4s


@pytest.fixture(scope="session")
def setup_splunk_sdk(splunk):
    tried = 0

    while True:
        try:
            c = client.connect(
                username=splunk["username"],
                password=splunk["password"],
                host=splunk["host"],
                port=splunk["port"],
            )
            break
        except ConnectionRefusedError:
            tried += 1
            if tried > 600:
                raise
            sleep(1)
    return c

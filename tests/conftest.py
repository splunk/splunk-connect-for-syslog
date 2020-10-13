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
    group = parser.getgroup("splunk-addon")

    group.addoption(
        "--sc4s_host",
        action="store",
        dest="sc4s_host",
        default="127.0.0.1",
        help="Address of the sc4s Server",
    )

    group.addoption(
        "--splunk_app",
        action="store",
        dest="splunk_app",
        default="package",
        help="Path to Splunk app",
    )
    group.addoption(
        "--splunk_type",
        action="store",
        dest="splunk_type",
        default="docker",
        help="Type of Splunk",
    )
    group.addoption(
        "--splunk_host",
        action="store",
        dest="splunk_host",
        default="127.0.0.1",
        help="Address of the Splunk Server",
    )
    group.addoption(
        "--splunk_port",
        action="store",
        dest="splunk_port",
        default="8089",
        help="Splunk rest port",
    )
    group.addoption(
        "--splunk_user",
        action="store",
        dest="splunk_user",
        default="admin",
        help="Splunk login user",
    )
    group.addoption(
        "--splunk_password",
        action="store",
        dest="splunk_password",
        default="Changed@11",
        help="Splunk password",
    )
    group.addoption(
        "--splunk_hec_token",
        action="store",
        dest="splunk_hec_token",
        default=str(uuid.uuid1()),
        help="Splunk HEC token",
    )
    group.addoption(
        "--splunk_version",
        action="store",
        dest="splunk_version",
        default="latest",
        help="Splunk version",
    )


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code != 500:
            return True
    except ConnectionError:
        return False


def is_responsive_splunk(splunk):
    try:
        client.connect(
            username=splunk["username"],
            password=splunk["password"],
            host=splunk["host"],
            port=splunk["port"],
        )
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Get an absolute path to the  `docker-compose.yml` file. Override this
    fixture in your tests if you need a custom location."""

    return os.path.join(str(pytestconfig.invocation_dir), "tests", "docker-compose.yml")


@pytest.fixture(scope="session")
def splunk(request):
    if request.config.getoption("splunk_type") == "external":
        request.fixturenames.append("splunk_external")
        splunk = request.getfixturevalue("splunk_external")
    elif request.config.getoption("splunk_type") == "docker":
        os.environ["SPLUNK_PASSWORD"] = request.config.getoption("splunk_password")
        os.environ["SPLUNK_HEC_TOKEN"] = request.config.getoption("splunk_hec_token")
        request.fixturenames.append("splunk_docker")
        splunk = request.getfixturevalue("splunk_docker")
    else:
        raise Exception

    yield splunk


@pytest.fixture(scope="session")
def sc4s(request):
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
def splunk_docker(request, docker_services):
    docker_services.start("splunk")
    port = docker_services.port_for("splunk", 8089)

    splunk = {
        "host": docker_services.docker_ip,
        "port": port,
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }

    docker_services.wait_until_responsive(
        timeout=180.0, pause=1.0, check=lambda: is_responsive_splunk(splunk)
    )

    return splunk


@pytest.fixture(scope="session")
def splunk_external(request):
    splunk = {
        "host": request.config.getoption("splunk_host"),
        "port": request.config.getoption("splunk_port"),
        "username": request.config.getoption("splunk_user"),
        "password": request.config.getoption("splunk_password"),
    }
    return splunk


@pytest.fixture(scope="session")
def sc4s_docker(docker_services):
    docker_services.start("sc4s")

    ports = {514:  docker_services.port_for("sc4s", 514),601:  docker_services.port_for("sc4s", 601)}

    for x in range(5000, 5015):
        ports.update({x: docker_services.port_for("sc4s", x)})

    return docker_services.docker_ip, ports


@pytest.fixture(scope="session")
def sc4s_external(request):
    ports = {514: 514, 601: 601}
    for x in range(5000, 5050):
        ports.update({x: x})

    return request.config.getoption("sc4s_host"), ports


@pytest.fixture()
def setup_sc4s(sc4s):
    return sc4s


@pytest.fixture(scope="session")
def setup_splunk(splunk):
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

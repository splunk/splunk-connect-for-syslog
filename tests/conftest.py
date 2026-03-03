# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import json
import logging
import os
from typing import Tuple
import shortuuid
from time import sleep
import random
import pytest
import requests
import splunklib.client as client
import subprocess
from filelock import FileLock

logger = logging.getLogger(__name__)


def cleanup_docker_containers(keepalive=False):
    """Cleanup Docker containers and volumes"""
    if keepalive:
        logger.info("Keepalive enabled, skipping Docker cleanup")
        return
        
    logger.info("Cleaning up Docker containers...")
    try:
        # Get the project root directory (parent of tests directory)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        compose_file = os.path.join(project_root, "tests", "docker-compose.yml")
        
        result = subprocess.run(
            ["docker", "compose", "-f", compose_file, "down", "-v"],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            logger.info("Docker cleanup completed successfully")
        else:
            logger.warning(f"Docker cleanup finished with warnings: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("Docker cleanup timed out after 30 seconds")
    except Exception as e:
        logger.error(f"Failed to cleanup Docker containers: {e}")


def pytest_sessionfinish(session, exitstatus):
    """
    Cleanup hook that runs after all tests complete (success or failure).
    This ensures Docker containers are stopped even if tests fail or are interrupted.
    """
    # Check if keepalive flag is set
    keepalive = session.config.getoption("--keepalive", default=False)
    cleanup_docker_containers(keepalive=keepalive)


@pytest.fixture
def get_host_key():
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    return host


@pytest.fixture(scope="function")
def get_pid():
    return random.randint(1000, 32000) # NOSONAR


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
        default="00000000-0000-0000-0000-0000000000000",
        help="Splunk HEC token",
    )
    group.addoption(
        "--splunk_version",
        action="store",
        dest="splunk_version",
        default="latest",
        help="Splunk version",
    )

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
        logger.warning("Splunk is unresponsive! Retrying...")
        return False


def is_responsive_sc4s(host: str, port: int) -> bool:
    """Check SC4S health endpoint"""
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
    except Exception as e:
        logger.debug(f"Health check failed: {e}")
        return False
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
        raise ValueError

    yield splunk

@pytest.fixture(scope="session")
def start_splunk_docker(request, docker_services):
    docker_services.start("splunk")
    try:
        port = docker_services.port_for("splunk", 8089)
        logger.info(port)
    except Exception as e:
        raise RuntimeError(
            f"Docker service 'splunk' failed to start or is not running: {e}"
        ) from e

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
def splunk_docker(request, worker_id, tmp_path_factory):
    if worker_id == "master":
        request.fixturenames.append("start_splunk_docker")
        splunk_docker = request.getfixturevalue("start_splunk_docker")
        return splunk_docker
    
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    fn = root_tmp_dir / "splunk_docker.json"
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            splunk_docker = json.loads(fn.read_text())
        else:
            request.fixturenames.append("start_splunk_docker")
            splunk_docker = request.getfixturevalue("start_splunk_docker")
            fn.write_text(json.dumps(splunk_docker))
    
    return splunk_docker

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
def start_sc4s_docker(docker_services, setup_splunk) -> Tuple[str, dict]:
    docker_services.start("sc4s")

    ports = {
        514: docker_services.port_for("sc4s", 514),
        601: docker_services.port_for("sc4s", 601),
    }

    ports.update({5514: docker_services.port_for("sc4s", 5514)})
    ports.update({5601: docker_services.port_for("sc4s", 5601)})
    ports.update({6000: docker_services.port_for("sc4s", 6000)})
    ports.update({6002: docker_services.port_for("sc4s", 6002)})
    ports.update({8080: docker_services.port_for("sc4s", 8080)})
    ports.update({9000: docker_services.port_for("sc4s", 9000)})
    ports.update({9001: docker_services.port_for("sc4s", 9001)})
    ports.update({9002: docker_services.port_for("sc4s", 9002)})

    docker_ip = docker_services.docker_ip
    health_port = ports[8080]

    # Wait for SC4S health endpoint to report healthy status
    logger.info("Waiting for SC4S health endpoint to be responsive...")
    docker_services.wait_until_responsive(
        timeout=180.0,
        pause=2.0,
        check=lambda: is_responsive_sc4s(docker_ip, health_port)
    )

    return docker_ip, ports

@pytest.fixture(scope="session")
def sc4s_docker(request, worker_id, tmp_path_factory):
    if worker_id == "master":
        request.fixturenames.append("start_sc4s_docker")
        sc4s_docker = request.getfixturevalue("start_sc4s_docker")
        return sc4s_docker
    
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / "sc4s_docker.json"
    
    with FileLock(str(fn) + ".lock"):
        if fn.is_file():
            data = json.loads(fn.read_text())
            # this type conversion is requried because json keys are strings
            # and in almost all tests we are refrencing the port by int e.g setup_sc4s[1][514]
            sc4s_docker = (data[0], {int(k): v for k, v in data[1].items()})
        else:
            request.fixturenames.append("start_sc4s_docker")
            sc4s_docker = request.getfixturevalue("start_sc4s_docker")
            fn.write_text(json.dumps(sc4s_docker))

    return sc4s_docker
        

@pytest.fixture(scope="session")
def sc4s_external(request):
    ports = {
        514: 514,
        601: 601,
        5514: 5514,
        5601: 5601,
        6000: 6000,
        6001: 6001,
        6002: 6002,
        9000: 9000,
        9001: 9001,
        9002: 9002,
    }

    return request.config.getoption("sc4s_host"), ports

@pytest.fixture(scope="session")
def setup_sc4s(request):
    if request.config.getoption("splunk_type") == "external":
        request.fixturenames.append("sc4s_external")
        sc4s = request.getfixturevalue("sc4s_external")
    elif request.config.getoption("splunk_type") == "docker":
        request.fixturenames.append("sc4s_docker")
        sc4s = request.getfixturevalue("sc4s_docker")
    else:
        raise ValueError

    yield sc4s

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

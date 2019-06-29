from jinja2 import Environment
import urllib.request

import random

import socket

import sys
from time import sleep
import splunklib.results as results
import splunklib.client as client
from time import sleep
import pytest

env = Environment(extensions=['jinja2_time.TimeExtension'])

@pytest.fixture
def setup_wordlist():

    word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
    response = urllib.request.urlopen(word_url)
    long_txt = response.read().decode()
    return long_txt.splitlines()

@pytest.fixture
def setup_splunk():
    tried=0
    while true:
        try:
            c = client.connect(username="admin", password="Changed@11", host="splunk", port="8089")
        except ConnectionRefusedError:
            tried +=1
            if tried>90:
                raise
            sleep(1)
    return c

def sendsingle(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('sc4s', 514)

    tried = 0
    try:

        sock.connect(server_address)
    except:
        if tried > 90:
            raise
        sleep(1)

    sock.sendall(str.encode(message))
    sock.close()

def splunk_single(service,search):
    kwargs_normalsearch = {"exec_mode": "normal"}
    tried = 0
    while True:
        job = service.jobs.create(search, **kwargs_normalsearch)

        # A normal search returns the job's SID right away, so we need to poll for completion
        while True:
            while not job.is_ready():
                pass
            stats = {"isDone": job["isDone"],
                     "doneProgress": float(job["doneProgress"]) * 100,
                     "scanCount": int(job["scanCount"]),
                     "eventCount": int(job["eventCount"]),
                     "resultCount": int(job["resultCount"])}

            if stats["isDone"] == "1":
                break
            sleep(2)

        # Get the results and display them
        resultCount = stats["resultCount"]
        eventCount = stats["eventCount"]
        if resultCount > 0 or tried>15:
            break
        else:
            tried += 1
            sleep(1)
    return resultCount, eventCount


def test_defaultroute(record_property,setup_wordlist,setup_splunk):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string("{{ mark }} {% now 'utc', '%b %d %H:%M:%S' %}.000z {{ host }} sc4s_default[0]: test\n")
    message = mt.render(mark="<111>1", host=host)

    sendsingle(message)

    st= env.from_string("search \"{{ host }}\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk,search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1



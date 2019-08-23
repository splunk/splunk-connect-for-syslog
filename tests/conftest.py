# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import os
import random
from time import sleep

import pytest
import splunklib.client as client
from .splunkutils import *


@pytest.fixture(scope="module")
def setup_wordlist():
    path_to_current_file = os.path.realpath(__file__)
    current_directory = os.path.split(path_to_current_file)[0]
    path_to_file = os.path.join(current_directory, "data/wordlist.txt")

    wordlist = [line.rstrip('\n') for line in open(path_to_file)]
    return wordlist


@pytest.fixture
def get_host_key(setup_wordlist):
    part1 = random.choice(setup_wordlist)
    part2 = random.choice(setup_wordlist)
    host = "{}-{}".format(part1, part2)

    return host


@pytest.fixture
def setup_splunk():
    tried = 0
    while True:
        try:
            c = client.connect(username="admin", password="Changed@11", host="splunk", port="8089")
            break
        except ConnectionRefusedError:
            tried += 1
            if tried > 600:
                raise
            sleep(1)

        resultcount=0
        while resultcount!=10:
            sleep(5)
            search = "search index=_internal | top 10"
            resultcount, eventcount = splunk_single(setup_splunk, search)


    return c

# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))


# <134>Jan 27 14:29:26 nasapi[19090] - log - set_config - INFO- success
testdata = [
    "{{ mark }}{{ bsd }} nasapi[19090] - log - {{ host }} - INFO- success",
]
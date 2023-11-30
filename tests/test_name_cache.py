# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import datetime
import time

from .timeutils import time_operations
from .sendmessage import sendsingle
from .splunkutils import  splunk_single


def test_name_cache(get_host_key, setup_splunk, setup_sc4s):
    """
    Send a log event without a valid host.
    Then send another log event with a valid host to generate name cache entry.
    Then send the first event again. It should be assigned host value from the cache,
    so the search result should be equal 2. 
    """
    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    epoch = epoch[:-7]

    message_no_host = f"<111> {bsd} CEF:0|Trend Micro|Deep Security Manager|0.0.0|600|User Signed In|3|src=10.52.116.160"
    message_with_host = f"<111> {bsd} {get_host_key} CEF:0|Trend Micro|Deep Security Manager|0.0.0|600|User Signed In|3|src=10.52.116.160"

    send_message = lambda message: sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    send_message(message_no_host)
    send_message(message_with_host)
    time.sleep(1) # time to save cache record
    send_message(message_no_host)
    time.sleep(1) # splunk_single() will wait for the first record only
                  # let's make sure that the second one gets time to be processed

    search = f'search _time="{epoch}" index=* host="{get_host_key}"'

    result_count, _ = splunk_single(setup_splunk, search)
    assert result_count == 2
# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random
import datetime
import re

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment()

# Function to insert a colon between the time and TZ offset (from -0800 to -08:00)
def insert_colon(string, integer):
    return string[0:integer] + ':' + string[integer:]

# Function to remove leading zero from TZ offsets less than 10 hours
def removeZero(tz):
    return re.sub(r'\b0+(\d)(?=:)', r'\1', tz)

def time_operations(dt):
    # Generate an ISO 8601 (RFC 5424) compliant timestamp with local timezone offset (2020-02-12T12:46:39.323-08:00)
    # See https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    iso = dt.astimezone().isoformat(sep='T', timespec='milliseconds')
    # Generate an BSD-style (RFC 3164) compliant timestamp with no timezone (Oct 25 13:08:00)
    bsd = dt.strftime("%b %d %H:%M:%S")

    # Other variants of timestamps needed for this log sample
    time = dt.strftime("%H:%M:%S")
    date = dt.strftime("%Y-%m-%d")
    # Insert colon in tzoffset string; normally just 'tzoffset = dt.astimezone().strftime("%z")'
    # Could use helper function above; e.g. 'tzoffset = insert_char(dt.astimezone().strftime("%z"), ":", 3)'
    tzoffset = removeZero(insert_colon((dt.astimezone().strftime("%z")), 3))

    # Derive epoch timestamp for use in search string
    # NOTE:  There are caveats with 'strftime("%s")', see references below

    # See https://stackoverflow.com/questions/11743019/convert-python-datetime-to-epoch-with-strftime
    # See https://docs.python.org/3/library/datetime.html#datetime-objects
    # Basically: Don't use 'utcnow()'

    # Strict way to get epoch as a string (rather than float) avoiding naive objects
    # epoch = dt.fromtimestamp(dt.timestamp()).strftime('%s')

    # Since datetime.now().astimezone() is aware, strftime() should be safe and form below OK
    # Trim last 3 digits of microsecond resolution to obtain milliseconds
    epoch = dt.astimezone().strftime("%s.%f")[:-7]

    return iso, bsd, time, date, tzoffset, epoch

# <111> Oct 25 13:08:00 fortiweb date=2013-10-07 time=11:30:53 devname=FortiWeb-A log_id=10000017 msg_id=000000001117 device_id=FVVM040000010871 vd="root" timezone="(GMT-5:00)Eastern Time(US & Canada)" type=event subtype="system" pri=information trigger_policy="" user=admin ui=GUI action=login status=success msg="User admin login successfully from GUI(172.20.120.47)"
def test_fortinet_fwb_event(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, epoch = time_operations(dt)

    mt = env.from_string(
        "{{ mark }} {{ bsd }} fortiweb date={{ date }} time={{ time }} devname={{ host }} log_id=10000017 msg_id=000000001117 device_id=FVVM040000010871 vd=\"root\" timezone=\"(GMT{{ tzoffset }})Region,City\" type=event subtype=\"system\" pri=information trigger_policy=\"\" user=admin ui=GUI action=login status=success msg=\"User admin login successfully from GUI(172.20.120.47)\"")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, date=date, tzoffset=tzoffset)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{epoch}} index=netops sourcetype=\"fwb_event\"")
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <111> Oct 25 13:08:00 fortiweb date=2013-10-07 time=11:30:53 devname=FortiWeb-A log_id=30000000 msg_id=000001351251 device_id=FV-1KD3A14800059 vd="root" timezone="(GMT-8:00)Pacific Time(US&Canada)" type=traffic subtype="http" pri=notice proto=tcp service=http status=success reason=none policy=Auto-policy src=10.0.8.103 src_port=8142 dst=10.20.8.22 dst_port=80 http_request_time=0 http_response_time=0 http_request_bytes=444 http_response_bytes=401 http_method=get http_url="/" http_host="10.0.8.22" http_agent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; " http_retcode=200 msg="HTTP GET request from 10.0.8.103:8142 to 10.20.8.22:80" srccountry="Reserved" content_switch_name="testa" server_pool_name="Auto-ServerFarm"
def test_fortinet_fwb_traffic(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, epoch = time_operations(dt)

    mt = env.from_string(
        "{{ mark }} {{ bsd }} fortiweb date={{ date }} time={{ time }} devname={{ host }} log_id=30000000 msg_id=000001351251 device_id=FV-1KD3A14800059 vd=\"root\" timezone=\"(GMT{{ tzoffset }})Region,City\" type=traffic subtype=\"http\" pri=notice proto=tcp service=http status=success reason=none policy=Auto-policy src=10.0.8.103 src_port=8142 dst=10.20.8.22 dst_port=80 http_request_time=0 http_response_time=0 http_request_bytes=444 http_response_bytes=401 http_method=get http_url=\"/\" http_host=\"10.0.8.22\" http_agent=\"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; \" http_retcode=200 msg=\"HTTP GET request from 10.0.8.103:8142 to 10.20.8.22:80\" srccountry=\"Reserved\" content_switch_name=\"testa\" server_pool_name=\"Auto-ServerFarm\"")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, date=date, tzoffset=tzoffset)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{epoch}} index=netfw sourcetype=\"fwb_traffic\"")
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

# <111> Oct 25 13:08:00 fortiweb date=2013-10-07 time=11:30:53 devname=FortiWeb-A log_id=20000010 msg_id=000139289631 device_id=FV-1KD3A15800072 vd="root" timezone="(GMT+8:00)Beijing,ChongQing,HongKong,Urumgi" type=attack subtype="waf_signature_detection" pri=alert trigger_policy="" severity_level=Medium proto=tcp service=http action=Alert policy="123" src=172.22.6.234 src_port=60554 dst=10.0.9.13 dst_port=80 http_method=get http_url="/preview.php?file==../" http_host="10.0.9.123" http_agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0" http_session_id=3B9864AEKNQSLLODNTILCG37M2FZ6A88 msg="[Signatures name: 123] [main class name: Generic Attacks(Extended)] [sub class name: Directory Traversal]: 060150002" signature_subclass="Directory Traversal" signature_id="060150002" srccountry="Reserved" content_switch_name="none" server_pool_name="123" false_positive_mitigation="none" log_type=LOG_TYPE_SCORE_SUM event_score=3 score_message="[score_type: total_score] [score_scope: TCP Session] [score_threshold: 5] [score_sum: 7]" entry_sequence="000139289630"
def test_fortinet_fwb_attack(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, epoch = time_operations(dt)

    mt = env.from_string(
        "{{ mark }} {{ bsd }} fortiweb date={{ date }} time={{ time }} devname={{ host }} log_id=20000010 msg_id=000139289631 device_id=FV-1KD3A15800072 vd=\"root\" timezone=\"(GMT{{ tzoffset }})Region,City\" type=attack subtype=\"waf_signature_detection\" pri=alert trigger_policy=\"\" severity_level=Medium proto=tcp service=http action=Alert policy=\"123\" src=172.22.6.234 src_port=60554 dst=10.0.9.13 dst_port=80 http_method=get http_url=\"/preview.php?file==../\" http_host=\"10.0.9.123\" http_agent=\"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0\" http_session_id=3B9864AEKNQSLLODNTILCG37M2FZ6A88 msg=\"[Signatures name: 123] [main class name: Generic Attacks(Extended)] [sub class name: Directory Traversal]: 060150002\" signature_subclass=\"Directory Traversal\" signature_id=\"060150002\" srccountry=\"Reserved\" content_switch_name=\"none\" server_pool_name=\"123\" false_positive_mitigation=\"none\" log_type=LOG_TYPE_SCORE_SUM event_score=3 score_message=\"[score_type: total_score] [score_scope: TCP Session] [score_threshold: 5] [score_sum: 7]\" entry_sequence=\"000139289630\"")
    message = mt.render(mark="<111>", bsd=bsd, host=host, time=time, date=date, tzoffset=tzoffset)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{epoch}} index=netids sourcetype=\"fwb_attack\"")
    search = st.render(host=host, epoch=epoch)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

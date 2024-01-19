# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape
import datetime
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single


env = Environment(autoescape=select_autoescape(default_for_string=False))

# <30>1 2012-12-07T21:44:04.875z t3-normaluser.i.vormetric.com vee-FS 0 CGP2603I [CGP@21513 sev="INFO" msg="Audit access" cat="\[AUDIT\]" pol="normaluser-only-aes256" uinfo="normaluser,uid=2001,gid=1" sproc="/usr/bin/cat" act="read_attr" gp="/export/home/normaluser/test" filePath="test.txt" denyStr="PERMIT" showStr="Code (1M)"]

@pytest.mark.addons("vormetric")
def test_vormetric(record_property, get_host_key, setup_splunk, setup_sc4s):
    host = get_host_key

    dt = datetime.datetime.now()
    timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.%fz")
    iso = dt.astimezone().isoformat(sep="T", timespec="microseconds")
    epoch = dt.astimezone().strftime("%s.%f")[:-7]
    
    mt = env.from_string(
        '{{ mark }}1 {{ timestamp }} {{ host }} vee-FS 0 CGP2603I [CGP@21513 sev="INFO" msg="Audit access" cat="\[AUDIT\]" pol="normaluser-only-aes256" uinfo="normaluser,uid=2001,gid=1" sproc="/usr/bin/cat" act="read_attr" gp="/export/home/normaluser/test" filePath="test.txt" denyStr="PERMIT" showStr="Code (1M)"]'
    )

    message = mt.render(mark="<30>", timestamp=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth  host={{ host }} sourcetype="thales:vormetric"'
    )
    search = st.render(
        epoch=epoch, host=host
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

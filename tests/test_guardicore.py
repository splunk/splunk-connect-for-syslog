# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import datetime
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


# <14>2025-12-22T17:17Z Guardicore CEF:0|Guardicore|Centra|51|Network Log|Network Log|None|...
# Guardicore uses ISO 8601 timestamps (YYYY-MM-DDTHH:MMZ) in the syslog header instead of
# the BSD-style MMM DD HH:MM:SS format required by RFC 3164.
@pytest.mark.addons("guardicore")
def test_guardicore_centra_almost_syslog(record_property, get_host_key, setup_splunk, setup_sc4s):
    host = "guardicore-" + get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)

    # Guardicore emits ISO 8601 without seconds: YYYY-MM-DDTHH:MMZ
    iso_no_seconds = dt.strftime("%Y-%m-%dT%H:%MZ")

    # Truncate to minute boundary because Guardicore timestamps have no seconds,
    # so the indexed event time will be at HH:MM:00
    dt_minute = dt.replace(second=0, microsecond=0)
    _, _, _, _, _, _, epoch = time_operations(dt_minute)
    epoch = epoch[:-7]

    mt = env.from_string(
        "<14>{{ timestamp }} {{ host }} CEF:0|Guardicore|Centra|51|Network Log|Network Log|None|"
        "id=cda17db8 act=Allowed cnt=1 start={{ timestamp }} src=1.1.1.1 shost=shost "
        "dst=1.1.1.1 dpt=53 dhost=Unknown proto=TCP cs1Label=connection_type cs1=SUCCESSFUL "
        "cs2Label=source_asset_labels cs2=os_type: AIX cs6Label=connection_verdict cs6=allowed "
        "cs7Label=policy_rule cs7=cs7 "
        "cs8Label=policy_ruleset cs8=AIX DNS Control"
    )
    message = mt.render(timestamp=iso_no_seconds, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops sourcetype="guardicore:centra:cef" host="{{ host }}" earliest={{ epoch }}'
    )
    search = st.render(host=host, epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
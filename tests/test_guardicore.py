# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

import shortuuid
from jinja2 import Environment, select_autoescape
import pytest

from tests.sendmessage import sendsingle
from tests.splunkutils import  splunk_single
from tests.timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))
#env = Environment()
#<14>2025-12-22T17:17Z Guardicore CEF:0|Guardicore|Centra|51|Network Log|Network Log|None|id=b858ea9c act=Allowed cnt=1 start=2025-12-22T17:07Z src=10.18.164.30 shost=papif-cmwebw08 dst=10.176.252.132 dpt=25 dhost=Unknown proto=TCP cs1Label=connection_type cs1=SUCCESSFUL cs2Label=source_asset_labels cs2=os_type: AIX,Application: IP10.121.96.105,Env: Nonprod,Agent: Installed cs6Label=connection_verdict cs6=allowed cs7Label=policy_rule cs7=default cs18Label=source_process_hash cs18=Unknown cs19Label=destination_process_hash cs19=Unknown cs20Label=source_node_type cs20=asset cs21Label=destination_node_type cs21=subnet

@pytest.mark.addons("checkpoint")
def test_guardicore_application_logs(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{ host }} ---- <14>2025-12-22T17:17Z Guardicore CEF:0|Guardicore|Centra|51|Network Log|Network Log|None|id=b858ea9c act=Allowed cnt=1 start=2025-12-22T17:07Z src=10.18.164.30 shost=papif-cmwebw08 dst=10.176.252.132 dpt=25 dhost=Unknown proto=TCP cs1Label=connection_type cs1=SUCCESSFUL cs2Label=source_asset_labels cs2=os_type: AIX,Application: IP10.121.96.105,Env: Nonprod,Agent: Installed cs6Label=connection_verdict cs6=allowed cs7Label=policy_rule cs7=default cs18Label=source_process_hash cs18=Unknown cs19Label=destination_process_hash cs19=Unknown cs20Label=source_node_type cs20=asset cs21Label=destination_node_type cs21=subnet'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=* host="{{ host }}" sourcetype="guardicore_log:syslog"'
    )
    search = st.render(epoch=epoch, bsd=bsd, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1



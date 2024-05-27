# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <134>1 2022-01-27T19:51:46Z host #ILO4 - - - Browser login: Administrator - 10.0.0.0(host.domain.local)
@pytest.mark.addons("hp")
def test_hpe_ilo_4(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{ host }} #ILO4 - - - Browser login: Administrator - 10.0.0.0(host.domain.local)\n"
    )
    message = mt.render(mark="<165>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="hpe:ilo"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

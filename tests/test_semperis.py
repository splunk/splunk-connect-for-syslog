# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("semperis")
def test_semperis(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ bsd }} {{ host }} Semperis.DSP [AdChanges@51802] [ForestId] 1111 [ChangeId] 1111 [PartitionNamingContext] DC=corpcert,DC=heb,DC=com [DistinguishedName] CN=krbtgt,CN=Users,DC=corpcert,DC=heb,DC=com [ClassName] user [AttributeName] msDS-SupportedEncryptionTypes [ObjectModificationType] ModifyObject [AttributeModificationType] Modify [LinkedValueDN]  [ValidUntil] {{ iso }} [OriginatingServer] {{ host }} [OriginatingTime] {{ iso }} [OriginatingUsers]  [OriginatingUserWorkstations]  [StringValueFrom] 327680 [StringValueTo] 327680  '
    )

    message = mt.render(mark="<110>", bsd=bsd, host=host, date=date, time=time, iso=iso)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops  host={{ host }} sourcetype="semperis:dsp"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

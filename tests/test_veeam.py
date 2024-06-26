import pytest

import shortuuid
from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <14>1 2024-06-11T14:08:02.823748+10:00 MYSERVER Veeam_MP - - [origin enterpriseId="3xxx3"] [categoryId=0 instanceId=10010 OibID="1a583aa0-84f0-4f63-8cc0-a2e25a3dxxxf" OriginalOibID="75ae4bc8-725b-4583-b8e6-c2dfcabxxxba" VmRef="d5692942-d615-d64b-2339-31e3c29xxx49" VmName="server.mydomain.com" ServerName="This server" DateTime="06/10/2024 14:32:17" IsCorrupted="True" Platform="6" StorageSize="28473884672" RepositoryID="1451444b-83fa-44ec-9965-a48dxxx954cd" IsFull="False" Version="1" Description="VM 'server.mydomain.com' restore point has been created."]
@pytest.mark.addons("veeam")
def test_veeam(record_property, setup_splunk, setup_sc4s):
    host = f"veeam-host-{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        """{{ mark }} {{ iso }} {{ host }} Veeam_MP - - [origin enterpriseId="3xxx3"] [categoryId=0 instanceId=10010 OibID="1a583aa0-84f0-4f63-8cc0-a2e25a3dxxxf" OriginalOibID="75ae4bc8-725b-4583-b8e6-c2dfcabxxxba" VmRef="d5692942-d615-d64b-2339-31e3c29xxx49" VmName="server.mydomain.com" ServerName="This server" DateTime="06/10/2024 14:32:17" IsCorrupted="True" Platform="6" StorageSize="28473884672" RepositoryID="1451444b-83fa-44ec-9965-a48dxxx954cd" IsFull="False" Version="1" Description="VM 'server.mydomain.com' restore point has been created."]"""
    )
    message = mt.render(mark="<14>1", host=host, bsd=bsd, iso=iso)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="veeam:vbr:syslog"'
    )
    search = st.render(
        epoch=epoch, bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

testdata_github_ent = [
    '{{mark}}{{ bsd }} {{ host }} {{ app }}: {"actor_ip":"11.12.13.14","from":"oauth_tokens#create","actor":"GitHub-Admin","actor_id":4,"user":"GitHub-Admin","user_id":4,"action":"oauth_access.create","created_at":1635226346160,"data":{"user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36","method":"POST","request_id":"0ffae1d1-2559-44e1-8e52-97ee3fe38a84","server_id":"eeb8aa01-853f-4263-9258-c062c0b333bb","request_category":"other","controller_action":"create","url":"https://10.11.12.13/settings/tokens","client_id":"1462950842.1635181704","referrer":"https://10.11.12.13/settings/tokens/new","device_cookie":null,"actor_session":1,"oauth_access_id":6,"application_id":0,"application_name":"postman","scopes":["admin:enterprise","admin:gpg_key","admin:org","admin:org_hook","admin:pre_receive_hook","admin:public_key","admin:repo_hook","delete:packages","delete_repo","gist","notifications","repo","site_admin","user","workflow","write:discussion","write:packages"],"accessible_org_ids":[],"token_last_eight":"5N1d1A7D","hashed_token":"l4q/mZnBHhCoEqslbnTousw/LhjZ30seQHDJ0ZujyKk=","_document_id":"za92SHZCezXszJQosM8uEQ","@timestamp":1635226346160,"operation_type":"create","category_type":"Other","actor_location":{"location":{"lat":0.0,"lon":0.0}}}}',
    '{{mark}}{{ bsd }} {{ host }} {{ app }}: {"actor_ip":"1.2.3.4","from":"pull_request_review_events#create","actor":"GitHub-Admin","actor_id":4,"org_id":null,"action":"pull_request_review.submit","created_at":1635884728508,"data":{"user_agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36","method":"PUT","request_id":"67703f7e-557e-4034-9139-1c5ba522732e","server_id":"6032343d-1dab-4e71-bdf0-3abe667f5a3e","request_category":"other","controller_action":"create","url":"https://10.11.12.13/GitHub-Admin/test/pull/2/reviews","client_id":"1462950842.1635181704","referrer":"https://10.11.12.13/GitHub-Admin/test/pull/2/files","device_cookie":null,"actor_session":1,"spammy":false,"pull_request_id":1,"body":"My comment","allowed":true,"business_id":null,"id":1,"state":1,"issue_id":2,"review_id":1,"_document_id":"IdMHh7Thhxch8EAWhfo9eg","@timestamp":1635884728508,"operation_type":"modify","category_type":"Resource Management","actor_location":{"location":{"lat":0.0,"lon":0.0}}}}',
]


@pytest.mark.addons("github")
@pytest.mark.parametrize("event", testdata_github_ent)
def test_data_github_ent(record_property,  setup_splunk, setup_sc4s, event):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<190>", bsd=bsd, host=host, app="github_audit")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=gitops _time={{ epoch }} sourcetype="github:enterprise:audit" source="github:enterprise:audit" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = mt.render(mark="", bsd="", host="", app="")
    message1 = message1.lstrip().replace('"', '\\"')[2:]
    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

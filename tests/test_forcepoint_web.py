# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])

#<134>Oct 16 12:13:06 sourcehost2 vendor=Websense 9f product=Security product_version=7.7.0 action=permitted severity=7 category=755 user=LDAP://user7 OU=Users,OU=Beijing,DC=com/TEST\, TEST_NAME src_host=10.0.0.4 src_port=61435 dst_host=HOST-013 dst_ip=10.0.0.19 dst_port=25404 bytes_out=4074 bytes_in=12328 http_response=200 http_method=POST http_content_type=image/gif;charset=UTF-8 http_user_agent=Mozilla/3.0 (Windows; U; Windows NT 6.1; es-def; rv:1.7.0.11) Gecko/2009060215 Firefox/8.0.11 (.NET CLR 8.5.30729) http_proxy_status_code=200 reason=- disposition=2573 policy=role-8**Default role=4 duration=63 url=http://test_web.com/contents/content1.jpg
def test_forcepoint_webprotect_kv(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'local', '%b %d %H:%M:%S' %} {{ host }} vendor=Websense 9f product=Security product_version=7.7.0 action=permitted severity=7 category=755 user=LDAP://user7 OU=Users,OU=Beijing,DC=com/TEST\, TEST_NAME src_host=10.0.0.4 src_port=61435 dst_host=HOST-013 dst_ip=10.0.0.19 dst_port=25404 bytes_out=4074 bytes_in=12328 http_response=200 http_method=POST http_content_type=image/gif;charset=UTF-8 http_user_agent=Mozilla/3.0 (Windows; U; Windows NT 6.1; es-def; rv:1.7.0.11) Gecko/2009060215 Firefox/8.0.11 (.NET CLR 8.5.30729) http_proxy_status_code=200 reason=- disposition=2573 policy=role-8**Default role=4 duration=63 url=http://test_web.com/contents/content1.jpg unknownfield=-\n")
    message = mt.render(mark="<134>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=netproxy host=\"{{ host }}\" sourcetype=\"websense:cg:kv\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
#<134>1 Dec 6 08:41:44 192.168.1.1 1 1386337316.207232138 MX84 events Cellular connection up

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

#<111> 2020-02-12,23:13:33,devname=FortiWeb-A,log_id=11005607,msg_id=000377260939,device_id=FV-1111111800222,vd=\"root\",\"timezone=\"\"(GMT+3:00)Kuwait,Riyadh\"\"\",type=event,subtype=\"system\",pri=notice,trigger_policy=\"Splunk_policy\",user=daemon,ui=daemon,action=check-resource,status=success,\"msg=\"\"The logdisk usage is too high\"\"\"
def test_fortinet_fwb_event(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'local', '%Y-%m-%d' %},{% now 'local', '%H:%M:%S' %},devname={{ host }},log_id=11005607,msg_id=000377260939,device_id=FV-1111111800222,vd=\"root\",\"timezone=\"\"(GMT+3:00)Kuwait,Riyadh\"\"\",type=event,subtype=\"system\",pri=notice,trigger_policy=\"Splunk_policy\",user=daemon,ui=daemon,action=check-resource,status=success,\"msg=\"\"The logdisk usage is too high\"\"\"\n")
    message = mt.render(mark="<13>", host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netops host=\"{{ host }}\" sourcetype=\"fwb_event\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
#<111> 2020-02-12,23:16:41,devname=FortiWeb-A,log_id=30001000,msg_id=000377262759,device_id=FV-1111111800222,vd="root","timezone=""(GMT+3:00)Kuwait,Riyadh""",type=traffic,subtype="https",pri=notice,proto=tcp,service=https/tls1.2,status=success,reason=none,policy=Phome_Policy,original_src=1.107.71.90,src=1.107.71.90,src_port=28799,dst=1.16.16.11,dst_port=80,http_request_time=0,http_response_time=0,http_request_bytes=623,http_response_bytes=15660,http_method=get,"http_url=""/publish/templates/images/bluebottom.jpg""","http_host=""splunk.infigo.hr""","http_agent=""Mozilla/5.0 (Linux; Android 9; SM-J415F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36""",http_retcode=200,"msg=""HTTPS get request from 1.107.71.90:28799 to 1.16.16.11:80""",original_srccountry="Saudi Arabia",srccountry="Saudi Arabia",content_switch_name="none",server_pool_name="PHOME","user_name=""Unknown""","http_refer=""https://splunk.infigo.hr/publish/templates/CSS/sc4s.css""",http_version="1.x",dev_id=none,cipher_suite="TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
def test_fortinet_fwb_traffic(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'local', '%Y-%m-%d' %},{% now 'local', '%H:%M:%S' %},devname={{ host }},log_id=30001000,msg_id=000377262759,device_id=FV-1111111800222,vd=\"root\",\"timezone=\"\"(GMT-8:00)Pacific Time(US&Canada)\"\"\",type=traffic,subtype=\"https\",pri=notice,proto=tcp,service=https/tls1.2,status=success,reason=none,policy=Phome_Policy,original_src=1.107.71.90,src=1.107.71.90,src_port=28799,dst=1.16.16.11,dst_port=80,http_request_time=0,http_response_time=0,http_request_bytes=623,http_response_bytes=15660,http_method=get,\"http_url=\"\"/publish/templates/images/bluebottom.jpg\"\"\",\"http_host=\"\"splunk.infigo.hr\"\"\",\"http_agent=\"\"Mozilla/5.0 (Linux; Android 9; SM-J415F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Mobile Safari/537.36\"\"\",http_retcode=200,\"msg=\"\"HTTPS get request from 1.107.71.90:28799 to 1.16.16.11:80\"\"\",original_srccountry=\"Saudi Arabia\",srccountry=\"Saudi Arabia\",content_switch_name=\"none\",server_pool_name=\"PHOME\",\"user_name=\"\"Unknown\"\"\",\"http_refer=\"\"https://splunk.infigo.hr/publish/templates/CSS/sc4s.css\"\"\",http_version=\"1.x\",dev_id=none,cipher_suite=\"TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384\"\n")
    message = mt.render(mark="<13>", host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netfw host=\"{{ host }}\" sourcetype=\"fwb_traffic\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<111> 2020-02-12,23:16:41,devname=FortiWeb-A,log_id=20000008,msg_id=000377262743,device_id=FV-1111111800222,vd="root","timezone=""(GMT+3:00)Kuwait,Riyadh""",type=attack,pri=alert,main_type="Signature Detection",sub_type="Information Disclosure",trigger_policy="",severity_level=Low,proto=tcp,service=https/tls1.2,backend_service=https/tls1.2,action=Alert,policy="MobApp_policy",src=1.70.8.51,src_port=20894,dst=1.16.220.15,dst_port=443,http_method=post,"http_url=""/mfp/api/abc""","http_host=""splunk.infigo.hr""","http_agent=""WLNativeAPI(HWSTK-HF; STK-L21MDV 9.1.0.336(C185E3R2P1); STK-L21; SDK 28; Android 9)""",http_session_id=ASDSADSA,"msg=""HTTP Header triggered signature ID 080200004 of Signatures policy Alert Only""",signature_subclass="HTTP Header Leakage",signature_id="080200004",signature_cve_id="N/A",srccountry="Kuwait",content_switch_name="none",server_pool_name="MObApp_pool",false_positive_mitigation="none","user_name=""Unknown""",monitor_status="Enabled","http_refer=""none""",http_version="1.x",dev_id="none",es=1,threat_weight=5,history_threat_weight=0,threat_level=Low,ftp_mode="N/A",ftp_cmd="N/A",cipher_suite="TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"ml_log_hmm_probability=0.000000,ml_log_sample_prob_mean=0.000000,ml_log_sample_arglen_mean=0.000000,ml_log_arglen=0,ml_svm_log_main_types=0,ml_svm_log_match_types="none",ml_svm_accuracy="none",ml_domain_index=0,ml_url_dbid=0,ml_arg_dbid=0,ml_allow_method="none",owasp_top10="A3:2017-Sensitive Data Exposure",bot_info="none",matched_field="header","matched_pattern=""X-Powered-By: Servlet/3.1"""
def test_fortinet_fwb_attack(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{ mark }}{% now 'local', '%Y-%m-%d' %},{% now 'local', '%H:%M:%S' %},devname={{ host }},log_id=20000008,msg_id=000377262743,device_id=FV-1111111800222,vd=\"root\",\"timezone=\"\"(GMT+3:00)Kuwait,Riyadh\"\"\",type=attack,pri=alert,main_type=\"Signature Detection\",sub_type=\"Information Disclosure\",trigger_policy=\"\",severity_level=Low,proto=tcp,service=https/tls1.2,backend_service=https/tls1.2,action=Alert,policy=\"MobApp_policy\",src=1.70.8.51,src_port=20894,dst=1.16.220.15,dst_port=443,http_method=post,\"http_url=\"\"/mfp/api/abc\"\"\",\"http_host=\"\"splunk.infigo.hr\"\"\",\"http_agent=\"\"WLNativeAPI(HWSTK-HF; STK-L21MDV 9.1.0.336(C185E3R2P1); STK-L21; SDK 28; Android 9)\"\"\",http_session_id=ASDSADSA,\"msg=\"\"HTTP Header triggered signature ID 080200004 of Signatures policy Alert Only\"\"\",signature_subclass=\"HTTP Header Leakage\",signature_id=\"080200004\",signature_cve_id=\"N/A\",srccountry=\"Kuwait\",content_switch_name=\"none\",server_pool_name=\"MObApp_pool\",false_positive_mitigation=\"none\",\"user_name=\"\"Unknown\"\"\",monitor_status=\"Enabled\",\"http_refer=\"\"none\"\"\",http_version=\"1.x\",dev_id=\"none\",es=1,threat_weight=5,history_threat_weight=0,threat_level=Low,ftp_mode=\"N/A\",ftp_cmd=\"N/A\",cipher_suite=\"TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256\"ml_log_hmm_probability=0.000000,ml_log_sample_prob_mean=0.000000,ml_log_sample_arglen_mean=0.000000,ml_log_arglen=0,ml_svm_log_main_types=0,ml_svm_log_match_types=\"none\",ml_svm_accuracy=\"none\",ml_domain_index=0,ml_url_dbid=0,ml_arg_dbid=0,ml_allow_method=\"none\",owasp_top10=\"A3:2017-Sensitive Data Exposure\",bot_info=\"none\",matched_field=\"header\",\"matched_pattern=\"\"X-Powered-By: Servlet/3.1\"\"\"\n")
    message = mt.render(mark="<13>", host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netids host=\"{{ host }}\" sourcetype=\"fwb_attack\" | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

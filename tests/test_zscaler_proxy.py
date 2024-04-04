# Copyright 2019 Splunk, Inc.
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

# Note the long white space is a \t
# 2019-10-16 15:44:36    reason=Allowed    event_id=6748427317914894361    protocol=HTTPS    action=Allowed    transactionsize=663    responsesize=65    requestsize=598    urlcategory=UK_ALLOW_Pharmacies    serverip=192.168.168.168    clienttranstime=0    requestmethod=CONNECT    refererURL=None    useragent=Windows Windows 10 Enterprise ZTunnel/1.0    product=NSS    location=UK_Wynyard_VPN->other    ClientIP=192.168.0.0    status=200    user=first.last@example.com    url=random@example.com:443    vendor=Zscaler    hostname=example@random.com    clientpublicIP=192.168.0.1    threatcategory=None    threatname=None    filetype=None    appname=RANDOM    pagerisk=0    department=Procurement, Generics    urlsupercategory=User-defined    appclass=Sales and Marketing    dlpengine=None    urlclass=Bandwidth Loss    threatclass=None    dlpdictionaries=None    fileclass=None    bwthrottle=NO    servertranstime=0    md5=None
@pytest.mark.addons("zscaler")
def test_zscaler_proxy(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, time, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = time[:-7]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ date }} {{ time }}\treason=Allowed\tevent_id=6748427317914894361\tprotocol=HTTPS\taction=Allowed\ttransactionsize=663\tresponsesize=65\trequestsize=598\turlcategory=UK_ALLOW_Pharmacies\tserverip=192.168.0.1\tclienttranstime=0\trequestmethod=CONNECT\trefererURL=None\tuseragent=Windows Windows 10 Enterprise ZTunnel/1.0\tproduct=NSS\tlocation=UK_Wynyard_VPN->other\tClientIP=192.168.0.38\tstatus=200\tuser=first.last@example.com\turl=random@example.com:443\tvendor=Zscaler\thostname={{host}}.random.com\tclientpublicIP=192.168.0.1\tthreatcategory=None\tthreatname=None\tfiletype=None\tappname=Random\tpagerisk=0\tdepartment=Procurement, Generics\turlsupercategory=User-defined\tappclass=Sales and Marketing\tdlpengine=None\turlclass=Bandwidth Loss\tthreatclass=None\tdlpdictionaries=None\tfileclass=None\tbwthrottle=NO\tservertranstime=0\tmd5=None"
    )
    message = mt.render(mark="<134>", date=date, time=time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalernss-web" hostname={{host}}.random.com'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# 2020-03-02 02:51:56	reason=Allowed	event_id=6799437957281873922	protocol=HTTP	action=Allowed	transactionsize=623	responsesize=512	requestsize=111	urlcategory=Internet Services	serverip=192.168.0.1	clienttranstime=3	requestmethod=GET	refererURL="None"	useragent=Microsoft NCSI	product=NSS	location=Road Warrior	ClientIP=192.168.0.1	status=200	user=random@example.com	url="www.msftconnecttest.com/connecttest.txt"	vendor=Zscaler	hostname=www.msftconnecttest.com	clientpublicIP=136.35.16.85	threatcategory=None	threatname=None	filetype=None	appname=generalbrowsing	pagerisk=0	department=Default Department	urlsupercategory=Internet Communication	appclass=General Browsing	dlpengine=None	urlclass=Business Use	threatclass=None	dlpdictionaries=None	fileclass=None	bwthrottle=NO	servertranstime=3	md5=None	contenttype=text/plain	trafficredirectmethod=Z_APP	rulelabel=None	ruletype=None	mobappname=None	mobappcat=None	mobdevtype=None	bwclassname=General Surfing	bwrulename=No Bandwidth Control	throttlereqsize=0	throttlerespsize=0	deviceappversion=1.5.1.8	devicemodel=20QF000CUS	devicemodel=20QF000CUS	devicename=mdutta	devicename=mdutta	deviceostype=Windows OS	deviceostype=Windows OS	deviceosversion=Windows 10 Enterprise	deviceplatform=	clientsslcipher=None	clientsslsessreuse=UNKNOWN	clienttlsversion=None	serversslsessreuse=UNKNOWN	servertranstime=3	srvcertchainvalpass=UNKNOWN	srvcertvalidationtype=None	srvcertvalidityperiod=None	srvocspresult=None	srvsslcipher=None	srvtlsversion=None	srvwildcardcert=UNKNOWN	serversslsessreuse="UNKNOWN"	dlpidentifier="0"	dlpmd5="None"	epochtime="1583117516"	filename="None"	filesubtype="None"	module="General Browsing"	productversion="5.7r.78.218665_84"	reqdatasize="0"	reqhdrsize="111"	respdatasize="22"	resphdrsize="490"	respsize="512"	respversion="1.1"	tz="GMT"
@pytest.mark.addons("zscaler")
def test_zscaler_proxy_new(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, time, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = time[:-7]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ date }} {{ time }}"
        + '	reason=Allowed	event_id=6799437957281873922	protocol=HTTP	action=Allowed	transactionsize=623	responsesize=512	requestsize=111	urlcategory=Internet Services	serverip=192.168.0.1	clienttranstime=3	requestmethod=GET	refererURL="None"	useragent=Microsoft NCSI	product=NSS	location=Road Warrior	ClientIP=192.168.0.1	status=200	user=example@random.com	url="www.msftconnecttest.com/connecttest.txt"	vendor=Zscaler	hostname={{host}}.fls.doubleclick.net	clientpublicIP=136.35.16.85	threatcategory=None	threatname=None	filetype=None	appname=generalbrowsing	pagerisk=0	department=Default Department	urlsupercategory=Internet Communication	appclass=General Browsing	dlpengine=None	urlclass=Business Use	threatclass=None	dlpdictionaries=None	fileclass=None	bwthrottle=NO	servertranstime=3	md5=None	contenttype=text/plain	trafficredirectmethod=Z_APP	rulelabel=None	ruletype=None	mobappname=None	mobappcat=None	mobdevtype=None	bwclassname=General Surfing	bwrulename=No Bandwidth Control	throttlereqsize=0	throttlerespsize=0	deviceappversion=1.5.1.8	devicemodel=20QF000CUS	devicemodel=20QF000CUS	devicename=mdutta	devicename=mdutta	deviceostype=Windows OS	deviceostype=Windows OS	deviceosversion=Windows 10 Enterprise	deviceplatform=	clientsslcipher=None	clientsslsessreuse=UNKNOWN	clienttlsversion=None	serversslsessreuse=UNKNOWN	servertranstime=3	srvcertchainvalpass=UNKNOWN	srvcertvalidationtype=None	srvcertvalidityperiod=None	srvocspresult=None	srvsslcipher=None	srvtlsversion=None	srvwildcardcert=UNKNOWN	serversslsessreuse="UNKNOWN"	dlpidentifier="0"	dlpmd5="None"	epochtime="1583117516"	filename="None"	filesubtype="None"	module="General Browsing"	productversion="5.7r.78.218665_84"	reqdatasize="0"	reqhdrsize="111"	respdatasize="22"	resphdrsize="490"	respsize="512"	respversion="1.1"	tz="GMT"'
    )
    message = mt.render(mark="<134>", date=date, time=time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalernss-web" hostname={{host}}.fls.doubleclick.net'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("zscaler")
def test_zscaler_proxy_pri(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, time, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    time = time[:-7]
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ date }} {{ time }}\treason=Allowed\tevent_id=6748427317914894362\tprotocol=HTTPS\taction=Allowed\ttransactionsize=663\tresponsesize=65\trequestsize=598\turlcategory=UK_ALLOW_Pharmacies\tserverip=216.58.204.70\tclienttranstime=0\trequestmethod=CONNECT\trefererURL=None\tuseragent=Windows Windows 10 Enterprise ZTunnel/1.0\tproduct=NSS\tlocation=UK_Wynyard_VPN->other\tClientIP=192.168.0.38\tstatus=200\tuser=first.last@example.com\turl=4171764.fls.doubleclick.net:443\tvendor=Zscaler\thostname={{host}}.fls.doubleclick.net\tclientpublicIP=213.86.221.94\tthreatcategory=None\tthreatname=None\tfiletype=None\tappname=DoubleClick\tpagerisk=0\tdepartment=Procurement, Generics\turlsupercategory=User-defined\tappclass=Sales and Marketing\tdlpengine=None\turlclass=Bandwidth Loss\tthreatclass=None\tdlpdictionaries=None\tfileclass=None\tbwthrottle=NO\tservertranstime=0\tmd5=None"
    )
    message = mt.render(mark="<134>", date=date, time=time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalernss-web" hostname={{host}}.fls.doubleclick.net'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <118>Mar  1 22:05:35 [10.225.64.143] ZscalerNSS: The NSS free memory has decreased to 1.40 GB which is below the recommended 1.55 GB {{host}}
@pytest.mark.addons("zscaler")
def test_zscaler_nss_alerts(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}{{ bsd }} [10.0.0.143] ZscalerNSS: The NSS free memory has decreased to 1.40 GB which is below the recommended 1.55 GB {{host}}"
    )
    message = mt.render(mark="<134>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops sourcetype="zscalernss-alerts" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# {"LogTimestamp": "Mon Mar  2 02:57:01 2020","Customer": "random, Inc.","SessionID": "qdLxaTYtMbsCQllNaCZ2","ConnectionID": "qdLxaTYtMbsCQllNaCZ2,aZcOpy7yN8iPncqmSuAv","InternalReason": "","ConnectionStatus": "active","IPProtocol": 6,"DoubleEncryption": 0,"Username": "exampler@random.com","ServicePort": 8384,"ClientPublicIP": "192.168.0.1","ClientPrivateIP": "","ClientLatitude": 00.000000,"ClientLongitude": 00.000000,"ClientCountryCode": "US","ClientZEN": "US-OH-8290","Policy": "Any Any Allow","Connector": "DFA Azure-2","ConnectorZEN": "US-OH-8290","ConnectorIP": "10.256.256.256","ConnectorPort": 00000,"Host": "10.256.256.256","Application": "RANDOM APP","AppGroup": "Dynamically Discovered Apps","Server": "0","ServerIP": "10.256.256.256","ServerPort": 0000,"PolicyProcessingTime": 120,"CAProcessingTime": 445,"ConnectorZENSetupTime": 46610,"ConnectionSetupTime": 47200,"ServerSetupTime": 22207,"AppLearnTime": 0,"TimestampConnectionStart": "2020-02-29T20:42:01.228Z","TimestampConnectionEnd": "","TimestampCATx": "2020-02-29T20:42:01.228Z","TimestampCARx": "2020-02-29T20:42:01.228Z","TimestampAppLearnStart": "","TimestampZENFirstRxClient": "","TimestampZENFirstTxClient": "","TimestampZENLastRxClient": "","TimestampZENLastTxClient": "","TimestampConnectorZENSetupComplete": "2020-02-29T20:42:01.275Z","TimestampZENFirstRxConnector": "","TimestampZENFirstTxConnector": "","TimestampZENLastRxConnector": "","TimestampZENLastTxConnector": "","ZENTotalBytesRxClient": 0,"ZENBytesRxClient": 0,"ZENTotalBytesTxClient": 0,"ZENBytesTxClient": 0,"ZENTotalBytesRxConnector": 0,"ZENBytesRxConnector": 0,"ZENTotalBytesTxConnector": 0,"ZENBytesTxConnector": 0,"Idp": "IDP Config"}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_zpa_app(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_time = dt.strftime("%a %b %d %H:%M:%S %Y")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{"LogTimestamp": "{{ lss_time }}'
        + '","Customer": "random, Inc.","SessionID": "qdLxaTYtMbsCQllNaCZ2","ConnectionID": "qdLxaTYtMbsCQllNaCZ2,aZcOpy7yN8iPncqmSuAv","InternalReason": "","ConnectionStatus": "active","IPProtocol": 6,"DoubleEncryption": 0,"Username": "exampler@random.com","ServicePort": 8384,"ClientPublicIP": "192.168.0.1","ClientPrivateIP": "","ClientLatitude": 00.000000,"ClientLongitude": 00.000000,"ClientCountryCode": "US","ClientZEN": "US-OH-8290","Policy": "Any Any Allow","Connector": "DFA Azure-2","ConnectorZEN": "US-OH-8290","ConnectorIP": "192.168.0.1","ConnectorPort": 00000,"Host": "10.256.256.256","Application": "Random","AppGroup": "Dynamically Discovered Apps","Server": "0","ServerIP": "{{host}}","ServerPort": 8384,"PolicyProcessingTime": 120,"CAProcessingTime": 445,"ConnectorZENSetupTime": 46610,"ConnectionSetupTime": 47200,"ServerSetupTime": 22207,"AppLearnTime": 0,"TimestampConnectionStart": "2020-02-29T20:42:01.228Z","TimestampConnectionEnd": "","TimestampCATx": "2020-02-29T20:42:01.228Z","TimestampCARx": "2020-02-29T20:42:01.228Z","TimestampAppLearnStart": "","TimestampZENFirstRxClient": "","TimestampZENFirstTxClient": "","TimestampZENLastRxClient": "","TimestampZENLastTxClient": "","TimestampConnectorZENSetupComplete": "2020-02-29T20:42:01.275Z","TimestampZENFirstRxConnector": "","TimestampZENFirstTxConnector": "","TimestampZENLastRxConnector": "","TimestampZENLastTxConnector": "","ZENTotalBytesRxClient": 0,"ZENBytesRxClient": 0,"ZENTotalBytesTxClient": 0,"ZENBytesTxClient": 0,"ZENTotalBytesRxConnector": 0,"ZENBytesRxConnector": 0,"ZENTotalBytesTxConnector": 0,"ZENBytesTxConnector": 0,"Idp": "IDP Config"}'
    )
    message = mt.render(mark="<134>", lss_time=lss_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-app" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <111>{"LogTimestamp": "Mon Mar  2 02:57:01 2020","Customer": "random, Inc.","SessionID": "qdLxaTYtMbsCQllNaCZ2","ConnectionID": "qdLxaTYtMbsCQllNaCZ2,aZcOpy7yN8iPncqmSuAv","InternalReason": "","ConnectionStatus": "active","IPProtocol": 6,"DoubleEncryption": 0,"Username": "example@random.com","ServicePort": 8384,"ClientPublicIP": "192.168.0.1","ClientPrivateIP": "","ClientLatitude": 00.000000,"ClientLongitude": -00.000000,"ClientCountryCode": "US","ClientZEN": "US-OH-8290","Policy": "Any Any Allow","Connector": "DFA Azure-2","ConnectorZEN": "US-OH-8290","ConnectorIP": "192.168.0.1","ConnectorPort": 00000,"Host": "192.168.0.1","Application": "DFA IP SPACE","AppGroup": "Dynamically Discovered Apps","Server": "0","ServerIP": "10.26.1.19","ServerPort": 8384,"PolicyProcessingTime": 120,"CAProcessingTime": 445,"ConnectorZENSetupTime": 46610,"ConnectionSetupTime": 47200,"ServerSetupTime": 22207,"AppLearnTime": 0,"TimestampConnectionStart": "2020-02-29T20:42:01.228Z","TimestampConnectionEnd": "","TimestampCATx": "2020-02-29T20:42:01.228Z","TimestampCARx": "2020-02-29T20:42:01.228Z","TimestampAppLearnStart": "","TimestampZENFirstRxClient": "","TimestampZENFirstTxClient": "","TimestampZENLastRxClient": "","TimestampZENLastTxClient": "","TimestampConnectorZENSetupComplete": "2020-02-29T20:42:01.275Z","TimestampZENFirstRxConnector": "","TimestampZENFirstTxConnector": "","TimestampZENLastRxConnector": "","TimestampZENLastTxConnector": "","ZENTotalBytesRxClient": 0,"ZENBytesRxClient": 0,"ZENTotalBytesTxClient": 0,"ZENBytesTxClient": 0,"ZENTotalBytesRxConnector": 0,"ZENBytesRxConnector": 0,"ZENTotalBytesTxConnector": 0,"ZENBytesTxConnector": 0,"Idp": "IDP Config"}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_zpa_app_pri(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_time = dt.strftime("%a %b %d %H:%M:%S %Y")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{mark}}{"LogTimestamp": "{{ lss_time }}'
        + '","Customer": "random, Inc.","SessionID": "qdLxaTYtMbsCQllNaCZ2","ConnectionID": "qdLxaTYtMbsCQllNaCZ2,aZcOpy7yN8iPncqmSuAv","InternalReason": "","ConnectionStatus": "active","IPProtocol": 6,"DoubleEncryption": 0,"Username": "example@random.com","ServicePort": 8384,"ClientPublicIP": "192.168.0.1","ClientPrivateIP": "","ClientLatitude": 00.000000,"ClientLongitude": 00.000000,"ClientCountryCode": "US","ClientZEN": "US-OH-8290","Policy": "Any Any Allow","Connector": "DFA Azure-2","ConnectorZEN": "US-OH-8290","ConnectorIP": "10.202.4.68","ConnectorPort": 35992,"Host": "10.26.1.19","Application": "DFA IP SPACE","AppGroup": "Dynamically Discovered Apps","Server": "0","ServerIP": "{{host}}","ServerPort": 8384,"PolicyProcessingTime": 120,"CAProcessingTime": 445,"ConnectorZENSetupTime": 46610,"ConnectionSetupTime": 47200,"ServerSetupTime": 22207,"AppLearnTime": 0,"TimestampConnectionStart": "2020-02-29T20:42:01.228Z","TimestampConnectionEnd": "","TimestampCATx": "2020-02-29T20:42:01.228Z","TimestampCARx": "2020-02-29T20:42:01.228Z","TimestampAppLearnStart": "","TimestampZENFirstRxClient": "","TimestampZENFirstTxClient": "","TimestampZENLastRxClient": "","TimestampZENLastTxClient": "","TimestampConnectorZENSetupComplete": "2020-02-29T20:42:01.275Z","TimestampZENFirstRxConnector": "","TimestampZENFirstTxConnector": "","TimestampZENLastRxConnector": "","TimestampZENLastTxConnector": "","ZENTotalBytesRxClient": 0,"ZENBytesRxClient": 0,"ZENTotalBytesTxClient": 0,"ZENBytesTxClient": 0,"ZENTotalBytesRxConnector": 0,"ZENBytesRxConnector": 0,"ZENTotalBytesTxConnector": 0,"ZENBytesTxConnector": 0,"Idp": "IDP Config"}'
    )
    message = mt.render(mark="<134>", lss_time=lss_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-app" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# {"LogTimestamp": "Mon Mar  2 02:57:05 2020","Customer": "Random, Inc.","Username": "example@random.com","SessionID": "lCINpOrrZlRANDOMP+E","SessionStatus": "ZPN_STATUS_AUTHENTICATED","Version": "1.5.1.8.191135","ZEN": "US-IL-8706","CertificateCN": "AJIDJDNBJDNkndkncmncPqV/YRQXe17aDzRf6Z0M1n7CU7UaQ=@random.com","PrivateIP": "","PublicIP": "256.256.254.256","Latitude": 00.000000,"Longitude": -00.000000,"CountryCode": "","TimestampAuthentication": "2020-02-27T13:04:55.000Z","TimestampUnAuthentication": "","TotalBytesRx": 46997613,"TotalBytesTx": 2232391,"Idp": "IDP Config","Hostname": "","Platform": "","ClientType": "zpn_client_type_zapp","TrustedNetworks": ,"TrustedNetworksNames": ,"SAMLAttributes": "{\"FirstName\":[\"Random\"],\"LastName\":[\"Example\"],\"Email\":[\"randexam@example.com\"],\"GroupName\":[\"zScaler_ZPA\"]}","PosturesHit": ,"PosturesMiss": ,"ZENLatitude": 00.000000,"ZENLongitude": -00.000000,"ZENCountryCode": "RN"}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_zpa_bba(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_time = dt.strftime("%a %b %d %H:%M:%S %Y")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{"LogTimestamp": "{{ lss_time }}'
        + '","ConnectionID":"6N9BHIHZrwrandom,dUPdoZAgr6vJKlv588GG","Exporter":"unset","TimestampRequestReceiveStart":"2020-03-01T22:39:30.679Z","TimestampRequestReceiveHeaderFinish":"2020-03-01T22:39:30.679Z","TimestampRequestReceiveFinish":"2020-03-01T22:39:30.680Z","TimestampRequestTransmitStart":"2020-03-01T22:39:30.680Z","TimestampRequestTransmitFinish":"2020-03-02T02:28:53.277Z","TimestampResponseReceiveStart":"2020-03-01T22:39:30.707Z","TimestampResponseReceiveFinish":"2020-03-02T02:28:53.309Z","TimestampResponseTransmitStart":"2020-03-01T22:39:30.707Z","TimestampResponseTransmitFinish":"2020-03-02T02:28:51.762Z","TotalTimeRequestReceive":1193,"TotalTimeRequestTransmit":13762597414,"TotalTimeResponseReceive":13762601379,"TotalTimeResponseTransmit":13761054628,"TotalTimeConnectionSetup":1037,"TotalTimeServerResponse":-13762570100,"Method":"GET","Protocol":"HTTPS","Host":"randomhost.example.com","URL":"/remoteDesktopGateway","UserAgent":"","XFF":"","NameID":"example@randomexample.com","StatusCode":101,"RequestSize":2246,"ResponseSize":3823185,"ApplicationPort":443,"ClientPublicIp":"256.256.256.256","ClientPublicPort":00000,"ClientPrivateIp":"","Customer":"{{host}}","ConnectionStatus":"zfce_mt_remote_disconnect","ConnectionReason":"BRK_MT_CLOSED_FROM_ASSISTANT"}'
    )
    message = mt.render(mark="<134>", lss_time=lss_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-bba" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#{"LogTimestamp":"Tue Dec  6 09:12:10 2022","Connector":"************","CPUUtilization":"2","SystemMemoryUtilization":"7","ProcessMemoryUtilization":"1","AppCount":"4","ServiceCount":"10","TargetCount":"10","AliveTargetCount":"7","ActiveConnectionsToPublicSE":"59","DisconnectedConnectionsToPublicSE":"0","ActiveConnectionsToPrivateSE":"0","DisconnectedConnectionsToPrivateSE":"0","TransmittedBytesToPublicSE":"347483188","ReceivedBytesFromPublicSE":"34109578","TransmittedBytesToPrivateSE":"0","ReceivedBytesFromPrivateSE":"0","AppConnectionsCreated":"2685","AppConnectionsCleared":"2662","AppConnectionsActive":"23","UsedTCPPortsIPv4":"108","UsedUDPPortsIPv4":"14","UsedTCPPortsIPv6":"1","UsedUDPPortsIPv6":"3","AvailablePorts":"63977","SystemMaximumFileDescriptors":"1597377","SystemUsedFileDescriptors":"1952","ProcessMaximumFileDescriptors":"512000","ProcessUsedFileDescriptors":"388","AvailableDiskBytes":"127528673280"}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_zpa_connector_metrics (
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_time = dt.strftime("%a %b %d %H:%M:%S %Y")
    epoch = epoch[:-7]

    mt = env.from_string('{"LogTimestamp":"{{ lss_time }}","Connector":"{{host}}","CPUUtilization":"2","SystemMemoryUtilization":"7","ProcessMemoryUtilization":"1","AppCount":"4","ServiceCount":"10","TargetCount":"10","AliveTargetCount":"7","ActiveConnectionsToPublicSE":"59","DisconnectedConnectionsToPublicSE":"0","ActiveConnectionsToPrivateSE":"0","DisconnectedConnectionsToPrivateSE":"0","TransmittedBytesToPublicSE":"347483188","ReceivedBytesFromPublicSE":"34109578","TransmittedBytesToPrivateSE":"0","ReceivedBytesFromPrivateSE":"0","AppConnectionsCreated":"2685","AppConnectionsCleared":"2662","AppConnectionsActive":"23","UsedTCPPortsIPv4":"108","UsedUDPPortsIPv4":"14","UsedTCPPortsIPv6":"1","UsedUDPPortsIPv6":"3","AvailablePorts":"63977","SystemMaximumFileDescriptors":"1597377","SystemUsedFileDescriptors":"1952","ProcessMaximumFileDescriptors":"512000","ProcessUsedFileDescriptors":"388","AvailableDiskBytes":"127528673280"}')
    message = mt.render(mark="<134>", lss_time=lss_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-connector" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# {"LogTimestamp": "Mon Mar  2 02:51:53 2020","Customer": "random, Inc.","SessionID": "NNz9t5AY1Rq5dzyLbNRB","SessionType": "ZPN_ASSISTANT_BROKER_CONTROL","SessionStatus": "ZPN_STATUS_AUTHENTICATED","Version": "19.102.2","Platform": "el7","ZEN": "US-NY-8180","Connector": "St RANDOM-1","ConnectorGroup": "St Random Connector","PrivateIP": "192.168.16.15","PublicIP": "192.168.0.1","Latitude": 00.000000,"Longitude": -00.000000,"CountryCode": "","TimestampAuthentication": "2020-02-27T07:03:53.689Z","TimestampUnAuthentication": "","CPUUtilization": 1,"MemUtilization": 16,"ServiceCount": 0,"InterfaceDefRoute": "eth0","DefRouteGW": "192.168.16.1","PrimaryDNSResolver": "192.168.16.16","HostUpTime": "1572630032","ConnectorUpTime": "1579500006","NumOfInterfaces": 2,"BytesRxInterface": 63778867197,"PacketsRxInterface": 669441337,"ErrorsRxInterface": 0,"DiscardsRxInterface": 1181261,"BytesTxInterface": 50473462713,"PacketsTxInterface": 492668679,"ErrorsTxInterface": 0,"DiscardsTxInterface": 0,"TotalBytesRx": 6979022,"TotalBytesTx": 47705494}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_zpa_connector(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_time = dt.strftime("%a %b %d %H:%M:%S %Y")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{"LogTimestamp": "{{ lss_time }}'
        + '","Customer": "{{host}}","SessionID": "NNz9t5AY1Rq5dzyLbNRB","SessionType": "ZPN_ASSISTANT_BROKER_CONTROL","SessionStatus": "ZPN_STATUS_AUTHENTICATED","Version": "19.102.2","Platform": "el7","ZEN": "US-NY-8180","Connector": "St RANDOM-1","ConnectorGroup": "St RANDOM Connector","PrivateIP": "192.168.16.15","PublicIP": "192.168.0.1","Latitude": 00.000000,"Longitude": -00.000000,"CountryCode": "","TimestampAuthentication": "2020-02-27T07:03:53.689Z","TimestampUnAuthentication": "","CPUUtilization": 1,"MemUtilization": 16,"ServiceCount": 0,"InterfaceDefRoute": "eth0","DefRouteGW": "192.168.16.1","PrimaryDNSResolver": "192.168.16.16","HostUpTime": "1572630032","ConnectorUpTime": "1579500006","NumOfInterfaces": 2,"BytesRxInterface": 63778867197,"PacketsRxInterface": 669441337,"ErrorsRxInterface": 0,"DiscardsRxInterface": 1181261,"BytesTxInterface": 50473462713,"PacketsTxInterface": 492668679,"ErrorsTxInterface": 0,"DiscardsTxInterface": 0,"TotalBytesRx": 6979022,"TotalBytesTx": 47705494}'
    )
    message = mt.render(mark="<134>", lss_time=lss_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-connector" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# {"LogTimestamp": "Fri May 31 17:34:48 2019","Customer": "ANZ Team/zdemo in beta","Username": "ZPA LSS Client","SessionID": "cKgzUERSLl09Y+ytH8v5","SessionStatus": "ZPN_STATUS_AUTHENTICATED","Version": "19.12.0-36-g87dad18","ZEN": "broker1b.pdx2","CertificateCN": "slogger1b.pdx2.zpabeta.net","PrivateIP": "","PublicIP": "192.168.0.1","Latitude": 00.000000,"Longitude": -00.000000,"CountryCode": "US","TimestampAuthentication": "2019-05-29T21:18:38.000Z","TimestampUnAuthentication": "","TotalBytesRx": 31274866,"TotalBytesTx": 25424152,"Idp": "Example IDP Config","Hostname": "DESKTOP-RANDOMHC","Platform": "windows","ClientType": "zpn_client_type_zapp","TrustedNetworks": "TN1_stc1","TrustedNetworksNames": "145248739466947538","SAMLAttributes": "myname:jdoe,myemail:jdoe@zscaler.com","PosturesHit": "sm-posture1,sm-posture2","PosturesMisses": "sm-posture11,sm-posture12","ZENLatitude": 00.000000,"ZENLongitude": -00.000000,"ZENCountryCode": ""}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_zpa_auth(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_time = dt.strftime("%a %b %d %H:%M:%S %Y")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{"LogTimestamp": "{{ lss_time }}'
        + '","Customer": "{{host}}","Username": "ZPA LSS Client","SessionID": "cKgzUERSLl09Y+ytH8v5","SessionStatus": "ZPN_STATUS_AUTHENTICATED","Version": "19.12.0-36-g87dad18","ZEN": "broker1b.pdx2","CertificateCN": "slogger1b.pdx2.zpabeta.net","PrivateIP": "","PublicIP": "192.168.0.1","Latitude": 00.000000,"Longitude": 00.000000,"CountryCode": "US","TimestampAuthentication": "2019-05-29T21:18:38.000Z","TimestampUnAuthentication": "","TotalBytesRx": 31274866,"TotalBytesTx": 25424152,"Idp": "Example IDP Config","Hostname": "DESKTOP-RANDOMHC","Platform": "windows","ClientType": "zpn_client_type_zapp","TrustedNetworks": "TN1_stc1","TrustedNetworksNames": "145248739466947538","SAMLAttributes": "myname:jdoe,myemail:jdoe@zscaler.com","PosturesHit": "sm-posture1,sm-posture2","PosturesMisses": "sm-posture11,sm-posture12","ZENLatitude": 00.000000,"ZENLongitude": -00.000000,"ZENCountryCode": ""}'
    )
    message = mt.render(mark="<134>", lss_time=lss_time, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-auth" "{{host}}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

# {"ModifiedTime":"","CreationTime":"2024-03-27T09:15:51.000Z","ModifiedBy":1441345282406,"RequestID":"6397hjkgbf-677b-4711-9b51-9711hjgkh10d8a","SessionID":"wrhjkdghjghfjhgsjfjgfj1l6s16u","AuditOldValue":"","AuditNewValue":"","AuditOperationType":"Sign Out","ObjectType":"Authentication","ObjectName":"","ObjectID":0,"CustomerID":1441345282406,"User":"user@user.com","ClientAuditUpdate":0}
@pytest.mark.addons("zscaler")
def test_zscaler_lss_audit(
    record_property,  setup_splunk, setup_sc4s
):
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    lss_audit_time = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    epoch = epoch[:-7]

    mt = env.from_string(
        '{"ModifiedTime":"","CreationTime":"{{ lss_audit_time }}","ModifiedBy":1441345282406,"RequestID":"6397hjkgbf-677b-4711-9b51-9711hjgkh10d8a","SessionID":"wrhjkdghjghfjhgsjfjgfj1l6s16u","AuditOldValue":"","AuditNewValue":"","AuditOperationType":"Sign Out","ObjectType":"Authentication","ObjectName":"","ObjectID":0,"CustomerID":1441345282406,"User":"user@user.com","ClientAuditUpdate":0}'
    )
    message = mt.render(mark="<134>", lss_audit_time=lss_audit_time)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy sourcetype="zscalerlss-zpa-audit"'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
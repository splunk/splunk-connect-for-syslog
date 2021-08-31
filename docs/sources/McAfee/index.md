# Vendor - McAfee

## Product - EPO

This source requires a TLS connection; in most cases enabling TLS and using the default port 6514 is adequate. 
The source is understood to require a valid certificate.

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/5085/                                                   |
| Product Manual | https://kc.mcafee.com/corporate/index?page=content&id=KB87927 |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| mcafee:epo:syslog | none |

### Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| policy_auditor_vulnerability_assessment        | Policy Auditor Vulnerability Assessment events |
| mcafee_agent                                   | McAfee Agent events | 
| mcafee_endpoint_security                       | McAfee Endpoint Security events |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| mcafee_epo     | epav          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_MCAFEE_EPO_TLS_PORT      | empty string      | Enable a TLS port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_MCAFEE_EPO | no | Enable archive to disk for this specific source |
| SC4S_DEST_MCAFEE_EPO_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_SOURCE_TLS_ENABLE | no | This must be set to yes so that SC4S listens for encrypted syslog from ePO

### Additional setup
You must create a certificate for the SC4S server to receive encrypted syslog from ePO. A self-signed certificate is fine. Generate a self-signed certificate on the SC4S host:

`openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout /opt/sc4s/tls/server.key -out /opt/sc4s/tls/server.pem`

Uncomment the following line in `/lib/systemd/system/sc4s.service` to allow the docker container to use the certificate:

`Environment="SC4S_TLS_DIR=-v   :/etc/syslog-ng/tls:z"`

### Troubleshooting
from the command line of the SC4S host, run this: `openssl s_client -connect localhost:6514`

The message:
```
socket: Bad file descriptor
connect:errno=9
```

indicates that SC4S is not listening for encrypted syslog. Note that a `netstat` may show the port open, but it is not accepting encrypted traffic as configured.

It may take several minutes for the syslog option to be available in the `registered servers` dropdown.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=mcafee:epo:syslog")
```

## Product - Web Gateway


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3009/                                                   |
| Product Manual | https://kc.mcafee.com/corporate/index?page=content&id=KB77988&actp=RSS |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| mcafee:wg:kv | none |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| mcafee_wg     | netproxy          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_MCAFEE_WG_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_MCAFEE_WG_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_MCAFEE_WG | no | Enable archive to disk for this specific source |
| SC4S_DEST_MCAFEE_WG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_SOURCE_TLS_ENABLE | no | This must be set to yes so that SC4S listens for encrypted syslog from Mcafee Web Gateway |
|


### Troubleshooting
from the command line of the SC4S host, run this: `openssl s_client -connect localhost:6514`

The message:
```
socket: Bad file descriptor
connect:errno=9
```

indicates that SC4S is not listening for encrypted syslog. Note that a `netstat` may show the port open, but it is not accepting encrypted traffic as configured.

It may take several minutes for the syslog option to be available in the `registered servers` dropdown.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=mcafee:wg:kv")
```
## Product - Network Security Platform

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Product Manual | https://docs.mcafee.com/bundle/network-security-platform-10.1.x-product-guide/page/GUID-373C1CA6-EC0E-49E1-8858-749D1AA2716A.html |

### Sourcetypes

| sourcetype | notes |
| ---------- | ----- |
| mcafee:nsp | none  |

### Source

| source              | notes                               |
| ------------------- | ----------------------------------- |
| mcafee:nsp:alert    | Alert/Attack Events                 |
| mcafee:nsp:audit    | Audit Event or User Activity Events |
| mcafee:nsp:fault    | Fault Events                        |
| mcafee:nsp:firewall | Firewall Events                     |

### Index Configuration

| key        | index      | notes |
| ---------- | ---------- | ----- |
| mcafee_nsp | netids     | none  |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable                        | default      | description                                                                                     |
| ------------------------------- | ------------ | ----------------------------------------------------------------------------------------------- |
| SC4S_LISTEN_MCAFEE_NSP_TCP_PORT | empty string | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_MCAFEE_NSP_UDP_PORT | empty string | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_MCAFEE_NSP         | no           | Enable archive to disk for this specific source                                                 |
| SC4S_DEST_MCAFEE_NSP_HEC        | no           | When Splunk HEC is disabled globally set to yes to enable this specific source                  |

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected

```
index=netids sourcetype=mcafee:nsp
```

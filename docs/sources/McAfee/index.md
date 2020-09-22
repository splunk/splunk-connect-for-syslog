# Vendor - McAfee

## Product - EPO

This source requires a TLS connection in most cases enabling TLS and using the default port 6514 is adequate. 
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

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=mcafee:epo:syslog")
```

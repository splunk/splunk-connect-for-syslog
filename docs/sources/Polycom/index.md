# Vendor - Polycom

## Product - RPRM

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                                              |
| Product Manual | unknown  |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| polycom:rprm:syslog |                                                                               |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| polycom_rprm        | polycom:rprm:syslog       | netops          | none          |


### Filter type

MSG Parse: This filter parses message content


### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_POLYCOM_RPRM_TCP_PORT    | empty string     | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers.  |
| SC4S_POLYCOM_RPRM_UDP_PORT    | empty string     | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers.  |
| SC4S_ARCHIVE_POLYCOM_RPRM | no | Enable archive to disk for this specific source |
| SC4S_DEST_POLYCOM_RPRM_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

One or two sourcetypes are included in Proofpoint PPS logs.  The search below will surface both of them:

```
index=<asconfigured> sourcetype=polycom:rprm:syslog| stats count by host
```

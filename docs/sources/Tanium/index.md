# Vendor - Tanium

## Product - All

This source requires a TLS connection; in most cases enabling TLS and using the default port 6514 is adequate. 
The source is understood to require a valid certificate.

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4439/                                                   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| tanium | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| tanium_syslog     | epintel          | none          |

### Filter type

MSG Parse: This filter parses message content
timestamp: When present the field ``Client-Time-UTC`` will be used as the time source

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_ARCHIVE_TANIUM_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_TANIUM_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_SOURCE_TLS_ENABLE | no | This must be set to yes so that SC4S listens for encrypted syslog from ePO

### Additional setup

NOTE: Tanium requires the use of IETF framing and should be configured to use port 601 (DEFAULT) or locally configured RFC6587 port. Use of any other port configuration will cause
data corruption.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=tanium*")
```

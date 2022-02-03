# Vendor - TINTRI

## Product - All

This source requires a TLS connection; in most cases enabling TLS and using the default port 6514 is adequate. 
The source is understood to require a valid certificate.

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                              |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| tintri | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| tintri_syslog     | infraops          | none          |

### Filter type

MSG Parse: This filter parses message content generic linux logs will use the os:nix sourcetype

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_ARCHIVE_TINTRI_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_TINTRI_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Additional setup

NOTE: TINTRI requires the use of IETF framing and should be configured to use port 601 (DEFAULT) or locally configured RFC6587 port. Use of any other port configuration will cause
data corruption.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=tintri*")
```

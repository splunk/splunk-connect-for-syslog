# Vendor - McAfee

## Product - EPO

Initial support for the syslog means of data collection is NOT supported by any
current Splunk TA; a custom TA is required

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | none                                                   |
| Product Manual | unknown                                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| mcafee_epo        | mcafee:epo:syslog sourcetype                                                                                                 |

### Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| Future        | source field will be updated in the future to identify record types                 |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| mcafee_epo     | epav          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_MCAFEE_EPO_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_MCAFEE_EPO_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_MCAFEE_EPO | no | Enable archive to disk for this specific source |
| SC4S_DEST_MCAFEE_EPO_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=mcafee:epo:syslog")
```

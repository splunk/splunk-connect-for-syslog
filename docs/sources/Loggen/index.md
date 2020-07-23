# Vendor - Syslog-ng

## Product -  syslog-ng loggen

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Product Manual | https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.16/administration-guide/87   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| syslogng:loggen | None                                                                                                    |


### Index Configuration

| key            | index          | notes          |
|----------------|----------------|----------------|
| syslogng_loggen | main          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SYSLOGNG_LOGGEN_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_SYSLOGNG_LOGGEN_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_SYSLOGNG_LOGGEN | no | Enable archive to disk for this specific source |
| SC4S_DEST_SYSLOGNG_LOGGEN_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=main sourcetype="syslogng:loggen"| stats count by host
```

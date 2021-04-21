# Vendor - HAProxy

## Product 


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3135/                                                   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| haproxy:tcp | Default syslog format |
| haproxy:splunk:http | Splunk's documented custom format. Note: detection is based on `client_ip` prefix in message |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| haproxy_syslog     | netlb         | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_HAPROXY_SYSLOG_RFC6587_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_HAPROXY_SYSLOG_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_HAPROXY_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_HAPROXY_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 




### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=haproxy*")
```

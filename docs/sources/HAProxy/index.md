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
| haproxy     | netlb         | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

None



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=haproxy*")
```

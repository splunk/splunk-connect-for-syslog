# HAProxy


## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3135/>                                                   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| haproxy:tcp | Default syslog format |
| haproxy:splunk:http | Splunk's documented custom format. Note: detection is based on `client_ip` prefix in message |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| haproxy_syslog     | netlb         | none          |

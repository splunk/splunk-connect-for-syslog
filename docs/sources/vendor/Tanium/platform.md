# Platform

This source requires a TLS connection; in most cases enabling TLS and using the default port 6514 is adequate.
The source is understood to require a valid certificate.

## Key facts

* MSG Format based filter
* Requires TLS and uses IETF Frames use port 5425 after TLS Configuration

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4439/>                                                   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| tanium | none |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| tanium_syslog     | epintel          | none          |


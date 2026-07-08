# Arcsight Microsoft Windows (CEF)

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | <https://github.com/splunk/splunk-add-on-for-cef>                                                              |
| Product Manual | <https://docs.imperva.com/bundle/cloud-application-security/page/more/log-configuration.htm>                                                        |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

## Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| CEFEventLog:System or Application Event     | Windows Application and System Event Logs                                                                                  |
| CEFEventLog:Microsoft Windows     | Windows Security Event Logs                                                                                 |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Microsoft_System or Application Event      | CEFEventLog:System or Application Event      | oswin          | none          |
| Microsoft_Microsoft Windows      | CEFEventLog:Microsoft Windows      | oswinsec         | none          |


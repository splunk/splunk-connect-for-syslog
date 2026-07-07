# Incapsula


## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | <https://github.com/splunk/splunk-add-on-for-cef>                                                              |
| Splunk Add-on Source Specific | <https://splunkbase.splunk.com/app/7034>                                                               |
| Product Manual | <https://docs.imperva.com/bundle/cloud-application-security/page/more/log-configuration.htm>                                                        |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

## Source

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| Imperva:Incapsula        | Common sourcetype                                                                                                 |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Incapsula_SIEMintegration      | Imperva:Incapsula      | netwaf          | none          |


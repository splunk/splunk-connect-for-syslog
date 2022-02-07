# Incapsula


## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | <https://bitbucket.org/SPLServices/ta-cef-for-splunk/downloads/>                                                              |
| Splunk Add-on Source Specific | <https://bitbucket.org/SPLServices/ta-cef-imperva-incapsula/downloads/>                                                               |
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


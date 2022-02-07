# Cloud App Security (MCAS)

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | <https://bitbucket.org/SPLServices/ta-cef-for-splunk/downloads/>                                                              |
| Splunk Add-on Source Specific | none |
| Product Manual | <https://docs.microsoft.com/en-us/cloud-app-security/siem>                                                |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

## Source

| source    | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| microsoft:cas       | Common sourcetype                                                                                                 |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| MCAS_SIEM_Agent      | microsoft:cas      | main          | none          |

# Carbon Black Protection

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | none                                                  |
| Splunk Add-on Source Specific | <https://bitbucket.org/SPLServices/ta-cef-imperva-incapsula/downloads/>                                                               |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

## Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| carbonblack:protection:cef       | Note this method of onboarding is not recommended for a more complete experience utilize the json format supported by he product with hec or s3                                                                            |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Carbon Black_Protection      | carbonblack:protection:cef      | epintel          | none          |

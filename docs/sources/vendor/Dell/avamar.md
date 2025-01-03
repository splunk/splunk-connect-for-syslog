# Dell Avamar

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                                                                      |
| Add-on Manual  | <https://www.delltechnologies.com/asset/en-us/products/data-protection/technical-support/docu91832.pdf> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:avamar:msc| None                                                                                                    |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_avamar_msc| dell:avamar:msc| netops         | none           |

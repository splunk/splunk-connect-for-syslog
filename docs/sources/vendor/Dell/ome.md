# Dell OME

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                                                                      |
| Add-on Manual  | <https://dl.dell.com/content/manual61620793-dell-openmanage-enterprise-4-6-user-s-guide.pdf?language=en-us> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:ome       | None                                                                                                    |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_ome_idrac | dell:ome       | infraops       | none           |

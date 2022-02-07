# iDrac

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                            |
| Add-on Manual | <https://www.dell.com/support/manuals/en-au/dell-opnmang-sw-v8.1/eemi_13g_v1.2-v1/introduction?guid=guid-8f22a1a9-ac01-43d1-a9d2-390ca6708d5e&lang=en-us>                                                    |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:poweredge:idrac:syslog        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_poweredge_idrac      | dell:poweredge:idrac:syslog     | infraops          | none          |


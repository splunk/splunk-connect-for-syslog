# PTA

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CyberArk | <https://splunkbase.splunk.com/app/2891/>                                                              |
| Add-on Manual | <https://docs.splunk.com/Documentation/AddOns/latest/CyberArk/About>                                                      |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cyberark:pta:cef        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Cyber-Ark_Vault      | cyberark:pta:cef      | main          | none          |


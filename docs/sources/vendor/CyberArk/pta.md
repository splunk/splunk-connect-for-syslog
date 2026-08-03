# PTA

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CyberArk | <https://splunkbase.splunk.com/app/2891/>                                                              |
| Add-on Manual | <https://docs.splunk.com/Documentation/AddOns/latest/CyberArk/About>                                                      |
| Product Manual | <https://docs.cyberark.com/pam-self-hosted/latest/en/content/pta/cef-based-format-definition.htm> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cyberark:pta:cef        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| CyberArk_PTA      | cyberark:pta:cef      | main          | none          |


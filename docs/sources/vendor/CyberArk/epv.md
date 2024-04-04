# Vendor - CyberArk

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514

## Product - EPV

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CyberArk | <https://splunkbase.splunk.com/app/2891/>                                                              |
| Add-on Manual | <https://docs.splunk.com/Documentation/AddOns/latest/CyberArk/About>                                                      |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cyberark:epv:cef        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Cyber-Ark_Vault      | cyberark:epv:cef      | netauth          | none          |


# Bastion

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3661/>                                                                 |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| WB:syslog  | note this sourcetype includes program:rdproxy all other data will be treated as nix  |

## Sourcetype and Index Configuration

| key                 | sourcetype             | index    | notes   |
|---------------------|------------------------|----------|---------|
| WB:syslog      | infraops      | main     | none    |


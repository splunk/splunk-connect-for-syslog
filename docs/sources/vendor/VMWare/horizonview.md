# Horizon View

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Manual | unknown |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| vmware:horizon:view | None |
| nix:syslog | When used with a default port this will follow the generic NIX configuration when using a dedicated port, IP or host rules events will follow the index configuration for vmware nsx  |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| vmware_horizon_view      | vmware:horizon:view | main          | none          |

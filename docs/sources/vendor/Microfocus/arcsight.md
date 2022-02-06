# Arcsight Internal Agent

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | <https://github.com/splunk/splunk-add-on-for-cef/downloads/>                                                              |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

## Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ArcSight:ArcSight        | Internal logs                                                                                               |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ArcSight_ArcSight      | ArcSight:ArcSight      | main          | none          |


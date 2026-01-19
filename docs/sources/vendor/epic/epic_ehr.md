# Epic EHR

## Key facts

* Requires vendor product by source configuration
* MSG Format based filter
* Legacy BSD Format default port 514
* RFC 5424 Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                                                                      |

## Sourcetypes

| sourcetype                  | notes                                                                                      |
|-----------------------------|--------------------------------------------------------------------------------------------|
| epic:epic-ehr:syslog        | None                                                                                       |

### Index Configuration

| key            | sourcetype           | index          | notes          |
|----------------|----------------------|----------------|----------------|
| epic_epic-ehr  | epic:epic-ehr:syslog | main           | none           |

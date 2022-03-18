# Enterprise Security RFC5424

## Key facts

* MSG Format based filter
* RFC5424

## Links

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | non                               |


## Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| kaspersky:syslog:es   | Where PROGRAM starts with KES                                                             |
| kaspersky:syslog   | None                                                             |

## Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| kaspersky_syslog         | kaspersky:syslog | epav          | none          |
| kaspersky_syslog_es         | kaspersky:syslog:es | epav          | none          |

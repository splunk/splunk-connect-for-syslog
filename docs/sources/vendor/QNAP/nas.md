# Nas

QNAP NAS QTS|QES shares a common syslog format.

## Key facts

* RFC3164
* Program based filter

## Links

| Ref            | Link                                     |
|----------------|------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4632> |

## Sourcetypes

| sourcetype     | notes           |
|----------------|-----------------|
| qnap:syslog    | QNAP NAS syslog |

## Sourcetype and Index Configuration

| key      | sourcetype     | index          | notes           |
|----------|----------------|----------------|-----------------|
| qnap_nas | qnap:syslog    | infraops       | none            |

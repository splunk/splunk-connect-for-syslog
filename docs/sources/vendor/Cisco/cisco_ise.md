## Cisco Identity Services Engine (ISE)

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/1915/>                                                                 |
| Product Manual | <https://www.cisco.com/c/en/us/td/docs/security/ise/2-6/Cisco_ISE_Syslogs/Cisco_ISE_Syslogs/Cisco_ISE_Syslogs_chapter_00.html> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:ise:syslog     | Aggregation used                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_ise     | cisco:ise:syslog    | netauth          | None     |

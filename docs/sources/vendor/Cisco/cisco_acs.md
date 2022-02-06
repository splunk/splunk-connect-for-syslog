# Cisco Access Control System (ACS)

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/1811/>                                                                 |
| Product Manual | <https://community.cisco.com/t5/security-documents/acs-5-x-configuring-the-external-syslog-server/ta-p/3143143> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:acs     | Aggregation used                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_acs    | cisco:acs    | netauth          | None     |

## Splunk Setup and Configuration

* Replace the following extract using Splunk local configuration. Impacts version 1.5.0 of the addond

```
EXTRACT-AA-signature = CSCOacs_(?<signature>\S+):?
# Note the value of this config is empty to disable
EXTRACT-AA-syslog_message = 
EXTRACT-acs_message_header2 = ^CSCOacs_\S+\s+(?<log_session_id>\S+)\s+(?<total_segments>\d+)\s+(?<segment_number>\d+)\s+(?<acs_message>.*)
```

# Symantec Endpoint Protection (SEPM)

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514
* KNOWN DATA LOSS ISSUE - The implementation of the syslog output component causes a "burst" behavior when run on schedule this burst can be larger than the udp buffer size on the source and or destination (sc4s) there is no possible workaround and the use of the Splunk Universal Forwarder to monitor file based output is recommended.

## Product - Symantec Endpoint Protection

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2772/                                                               |
| Product Manual | https://techdocs.broadcom.com/content/broadcom/techdocs/us/en/symantec-security-software/endpoint-security-and-management/endpoint-protection/all/Monitoring-Reporting-and-Enforcing-Compliance/viewing-logs-v7522439-d37e464/exporting-data-to-a-syslog-server-v8442743-d15e1107.html |


## Sourcetypes

| sourcetype                     | notes                                                                                                   |
|--------------------------------|---------------------------------------------------------------------------------------------------------|
| symantec:ep:syslog             | Warning the syslog method of accepting EP logs has been reported to show high data loss and is not Supported by Splunk  |
| symantec:ep:admin:syslog       | none |
| symantec:ep:agent:syslog       | none |
| symantec:ep:agt:system:syslog  | none |
| symantec:ep:behavior:syslog    | none |
| symantec:ep:packet:syslog      | none |
| symantec:ep:policy:syslog      | none |
| symantec:ep:proactive:syslog   | none |
| symantec:ep:risk:syslog        | none |
| symantec:ep:scan:syslog        | none |
| symantec:ep:scm:system:syslog  | none |
| symantec:ep:security:syslog    | none |
| symantec:ep:traffic:syslog     | none |

## Index Configuration

| key            | index          | notes          |
|----------------|----------------|----------------|
| symantec_ep    | epav           | none           |

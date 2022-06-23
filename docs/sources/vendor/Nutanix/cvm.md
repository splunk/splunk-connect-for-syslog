# Nutanix_CVM_Audit

## Key facts

* MSG Format based filter
* Community requested filter
* Only CVM log supported


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype           | notes                                                                                |
|----------------------|--------------------------------------------------------------------------------------|
| nutanix:syslog       | CVM logs                                                                             |
| nutanix:syslog:audit | CVM system audit logs   Considering the message host format is default ntnx-xxxx-cvm |

## Sourcetype and Index Configuration

| key                  | sourcetype           | index    | notes          |
|----------------------|----------------------|----------|----------------|
| nutanix_syslog       | nutanix:syslog       | infraops | none          |
| nutanix_syslog_audit | nutanix:syslog:audit | infraops | none          |

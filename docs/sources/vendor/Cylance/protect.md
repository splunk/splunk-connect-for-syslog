# Protect


## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CyberArk | <https://splunkbase.splunk.com/app/3709/>                                                              |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| syslog_protect        | Catchall                                                                                             |
| syslog_threat_classification        | None                                                                                                |
| syslog_audit_log        | None                                                                                                |
| syslog_exploit        | None                                                                                                |
| syslog_app_control        | None                                                                                                |
| syslog_threat        | None                                                                                                |
| syslog_device        | None                                                                                                |
| syslog_device_control        | None                                                                                                |
| syslog_script_control        | None                                                                                                |
| syslog_optics        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cylance_protect      | syslog_protect     | epintel          | none          |
| cylance_protect_auditlog      | syslog_audit_log     | epintel          | none          |
| cylance_protect_threatclassification      | syslog_threat_classification     | epintel          | none          |
| cylance_protect_exploitattempt      | syslog_exploit     | epintel          | none          |
| cylance_protect_appcontrol      | syslog_app_control     | epintel          | none          |
| cylance_protect_threat      | syslog_threat     | epintel          | none          |
| cylance_protect_device      | syslog_device     | epintel          | none          |
| cylance_protect_devicecontrol      | syslog_device_control     | epintel          | none          |
| cylance_protect_scriptcontrol      | syslog_protect     | epintel          | none          |
| cylance_protect_scriptcontrol      | syslog_script_control     | epintel          | none          |
| cylance_protect_optics      | syslog_optics     | epintel          | none          |


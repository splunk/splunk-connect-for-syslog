# Veeam

## Key facts

* MSG Format based filter
* rfc5424 default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on | <https://splunkbase.splunk.com/app/7312/>                                                              |
| User Guide | <https://helpcenter.veeam.com/docs/backup/vsphere/overview.html?ver=120>                                                              |
## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| veeam_vbr_syslog        | sourcetype decided considering the Veeam Splunk Add-on                                                                                               |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| veeam_veeam      | veeam_vbr_syslog      | infraops          | none          |

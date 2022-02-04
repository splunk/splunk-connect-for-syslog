# Vendor - Thycotic


## Product - Secret Server

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4060/                                                                 |
| Product Manual |                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| thycotic:syslog       | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Thycotic Software_Secret Server      | thycotic:syslog       | netauth          | none          |

### Filter type

CEF

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=thycotic:syslog  | stats count by host
```
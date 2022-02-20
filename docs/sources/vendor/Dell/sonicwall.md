# Sonicwall

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4507/                                                            |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:sonicwall        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_sonicwall-firewall      | dell:sonicwall     | netfw          | none          |


## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_DEST_DELL_SONICWALL-FIREWALL_SPLUNK_HEC_FMT | JSON | Restructure data from vendor format to json for splunk destinations set to "NONE" for native format |
| SC4S_DEST_DELL_SONICWALL-FIREWALL_SYSLOG_FMT | SDATA | Restructure data from vendor format to SDATA for SYSLOG destinations set to "NONE" for native format|

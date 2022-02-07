# Symantec DLP 

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on Symatec DLP | https://splunkbase.splunk.com/app/3029/                                                      |
| Add-on Manual | http://docs.splunk.com/Documentation/AddOns/latest/SymantecDLP/About                                     |


## Sourcetypes

| sourcetype           | notes                                                                                                   |
|----------------------|---------------------------------------------------------------------------------------------------------|
| symantec:dlp:syslog  | None                                                                                                    |

## Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| symantec_dlp   | symantec:dlp:syslog      | netauth          | none          |


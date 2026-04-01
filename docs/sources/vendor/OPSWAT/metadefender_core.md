# Metadefender Core

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | https://www.opswat.com/docs/mdcore/configuration/syslog-message-format  |


## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| 	opswat:mscl:cef        | None
| 	opswat:mscw:cef        | None                                                                                                     |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| opswat_mscl_cef     | opswat:mscl:cef       | netwaf          | none          |
| opswat_mscw_cef     | opswat:mscw:cef       | netwaf          | none          |

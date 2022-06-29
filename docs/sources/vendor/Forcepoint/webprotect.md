
# Webprotect (Websense) 

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2966/>                                                                 |
| Product Manual | <http://www.websense.com/content/support/library/web/v85/siem/siem.pdf>                                                        |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| websense:cg:kv        | None    |

## Sourcetype and Index Configuration

| key                   | sourcetype     | index          | notes                                                                                                   |
|-----------------------|----------------|----------------|---------------------------------------------------------------------------------------------------------|
| forcepoint_webprotect | websense:cg:kv       | netproxy          | none                                                                                                    |
| forcepoint_<random>   | websense:cg:kv       | netproxy          | if the log is in format of  vendor=Forcepoint product=<random> , the key will will be forcepoint_random |


# SIP Manager

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514/UDP
* Vendor source is not conformant to RFC3194 by improperly sending unescaped `\n` Use of TCP will cause dataloss

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| avaya:avaya        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| avaya_sipmgr      | avaya:avaya       | main          | none          |


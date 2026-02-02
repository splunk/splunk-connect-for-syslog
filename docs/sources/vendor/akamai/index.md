# Akamai Guardicore

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514/UDP
* Vendor source is not conformant to RFC3194 by improperly sending unescaped `\n` Use of TCP will cause dataloss

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/7426                                |
| Product Manual | unknown   |


## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| akami:guardicore:cef  | None                                                                                                    |

## Sourcetype and Index Configuration

| key               | sourcetype              | index          | notes          |
|-------------------|-------------------------|----------------|----------------|
| akamai_guardicore | akamai:guardicore:cef   | guardicore     | none          |


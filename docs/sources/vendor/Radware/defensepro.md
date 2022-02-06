#  DefensePro

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | Note this add-on does not provide functional extractions <https://splunkbase.splunk.com/app/4480/>                                                  |
| Product Manual | <https://www.radware.com/products/defensepro/> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| radware:defensepro  | Note some events do not contain host |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| radware_defensepro      | radware:defensepro     | netops          | none          |


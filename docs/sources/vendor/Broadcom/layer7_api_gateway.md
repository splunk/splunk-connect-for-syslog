# Layer7 API Gateway

Broadcom Layer7 API Gateway. The on-wire program is `SSG` and the traffic-logger output is identified by the category `com.l7tech.traffic`.

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                            |
| Product Manual | <https://techdocs.broadcom.com/us/en/ca-enterprise-software/layer7-api-management/api-gateway/11-2/reference.html> |

## Sourcetypes

| sourcetype                     | notes                                                                                                   |
|--------------------------------|---------------------------------------------------------------------------------------------------------|
| broadcom:layer7_api_gateway    | Field extraction is left to search-time in Splunk; the original log line is preserved.                  |

### Index Configuration

| key                          | index   | notes |
|------------------------------|---------|-------|
| broadcom_layer7_api_gateway  | netops  | none  |

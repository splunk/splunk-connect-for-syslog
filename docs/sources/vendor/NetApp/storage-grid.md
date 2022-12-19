# StorageGRID

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514
* Community requested parser


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3895/>                                  |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype           | notes                                                                                |
|----------------------|--------------------------------------------------------------------------------------|
| grid:auditlog       | None                                                                             |
| grid:rest:api | None |

## Sourcetype and Index Configuration

| key                  | sourcetype           | index    | notes          |
|----------------------|----------------------|----------|----------------|
| netapp_grid       | grid:auditlog       | infraops | none          |
| netapp_grid | grid:rest:api | infraops | none          |

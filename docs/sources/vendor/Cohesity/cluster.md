# Cluster

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype                             | notes                                                                           |
|----------------------------------------|---------------------------------------------------------------------------------|
| cohesity:cluster:audit                 | None                                                                            |
| cohesity:cluster:dataprotection        | None                                                                            |
| cohesity:api:audit                     | None                                                                            |


## Sourcetype and Index Configuration

| key                            | sourcetype                     | index          | notes          |
|--------------------------------|--------------------------------|----------------|----------------|
| cohesity_cluster_audit         | cohesity:cluster:audit         | infraops       | none           |
| cohesity_api_audit             | cohesity:api:audit             | infraops       | none           |
| cohesity_cluster_dataprotection| cohesity:cluster:dataprotection| infraops       | none           |


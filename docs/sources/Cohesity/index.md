# Vendor - Cohesity


## Product - Switches

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cohesity:cluster:audit        | None                                                                                                    |
| cohesity:cluster:dataprotection        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cohesity_cluster_audit        | cohesity:cluster:audit         | infraops          | none          |
| cohesity_cluster_dataprotection      | cohesity:cluster:dataprotection       | infraops          | none          |

### Filter type

MSG Parsing

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_COHESITY_CLUSTER_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_COHESITY_CLUSTER_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_COHESITY_CLUSTER | no | Enable archive to disk for this specific source |
| SC4S_DEST_COHESITY_CLUSTER_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=cohesity:cluster:* | stats count by host
```

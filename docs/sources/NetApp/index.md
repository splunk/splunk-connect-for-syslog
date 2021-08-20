# Vendor - NetApp


## Product - OnTap


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3418/                                                  |
| Product Manual | unknown |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| netapp:ems  | None |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| netapp_ontap      | netapp:ems     | infraops          | none          |

### Filter type

MSG Parsing

### Setup and Configuration



### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_NETAPP_ONTAP_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_NETAPP_ONTAP_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_NETAPP_ONTAP | no | Enable archive to disk for this specific source |
| SC4S_DEST_NETAPP_ONTAP_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

```
index=<asconfigured> sourcetype=netapp:ems | stats count by host
```

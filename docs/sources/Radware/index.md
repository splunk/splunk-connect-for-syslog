# Vendor - Radware


## Product - DefensePro


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | Note this add-on does not provide functional extractions https://splunkbase.splunk.com/app/4480/                                                  |
| Product Manual | https://www.radware.com/products/defensepro/ |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| radware:defensepro  | Note some events do not contain host |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| radware_defensepro      | radware:defensepro     | netops          | none          |

### Filter type

MSG Parsing

### Setup and Configuration



### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_RADWARE_DEFENSEPRO_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_RADWARE_DEFENSEPRO_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_RADWARE_DEFENSEPRO | no | Enable archive to disk for this specific source |
| SC4S_DEST_RADWARE_DEFENSEPRO_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=radware:defensepro | stats count by host
```

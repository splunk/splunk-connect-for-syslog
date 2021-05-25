# Vendor - Sophos


## Product - Web Appliance

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| sohpos:webappliance        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| sohpos_webappliance        | sohpos:webappliance         | netproxy          | none          |

### Filter type

Must use port or NETMASK/host

Configure vendor_product_by_source 

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SOPHOS_WEBAPPLIANCE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_SOPHOS_WEBAPPLIANCE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_SOPHOS_WEBAPPLIANCE | no | Enable archive to disk for this specific source |
| SC4S_DEST_SOPHOS_WEBAPPLIANCE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=sohpos:webappliance | stats count by host
```

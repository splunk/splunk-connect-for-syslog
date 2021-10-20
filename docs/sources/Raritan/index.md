# Vendor - Raritan


## Product - DSX


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                     |
| Product Manual | https://www.raritan.com/products/kvm-serial/serial-console-servers/serial-over-ip-console-server |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| raritan:dsx  | Note events do not contain host |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| raritan_dsx      | raritan:dsx     | infraops          | none          |

### Filter type

Requires port or vendor product by source config

### Setup and Configuration

unknown

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_RARITAN_DSX_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_RARITAN_DSX_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_RARITAN_DSX | no | Enable archive to disk for this specific source |
| SC4S_DEST_RARITAN_DSX_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=raritan:dsx | stats count by host
```

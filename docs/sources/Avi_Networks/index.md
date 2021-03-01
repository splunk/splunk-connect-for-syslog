# Vendor - Avi Networks


## Product - Switches

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | https://avinetworks.com/docs/latest/syslog-formats/   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| avi:events        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| avi_vantage     | avi:events       | netops          | none          |

### Filter type

Must be identified by host or ip assignment. Update the filter `f_brocade_syslog` or configure a dedicated port as required

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_AVI_VANTAGE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_AVI_VANTAGE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_AVI_VANTAGE | no | Enable archive to disk for this specific source |
| SC4S_DEST_AVI_VANTAGE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=avi:events| stats count by host
```

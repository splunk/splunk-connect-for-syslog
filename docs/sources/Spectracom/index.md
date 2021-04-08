# Vendor - Spectracom


## Product - NTP Appliance

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| spectracom:ntp        | None                                                                                                    |
| nix:syslog | None |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| spectracom_ntp      | spectracom:ntp       | netops          | none          |

### Filter type

Must use port or NETMASK and MSG Parsing

This appliance is a general purpose linux based OS providing time services. the time server application will be source typed as above while the OS level logs will be
processed as nix:syslog

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SPECTRACOM_NTP_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_SPECTRACOM_NTP_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_SPECTRACOM_NTP | no | Enable archive to disk for this specific source |
| SC4S_DEST_SPECTRACOM_NTP_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=spectracom:ntp | stats count by host
```

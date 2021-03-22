# Vendor - HPE
## Product - Aruba Clearpass


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| aruba:clearpass | Dynamically  Created |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| aruba_clearpass     | print          | none          |

### Filter type

Partial MSG Parse: This filter parses message content for events with a syslog "program" prefix "CPPM_". For complete parsing a dedicated port or vendor_product_by_source entry must be added


### Options


| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_ARUBA_CLEARPASS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_ARUBA_CLEARPASS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_ARUBA_CLEARPASS | no | Enable archive to disk for this specific source |
| SC4S_DEST_ARUBA_CLEARPASS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=aruba*")
```
## Product - JetDirect


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| hpe:jetdirect | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| hpe_jetdirect     | print          | none          |

### Filter type

MSG Parse: This filter parses message content


### Options

Note listed for reference processing utilizes the Microsoft ArcSight log path as this format is a subtype of CEF

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_HPE_JETDIRECT_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_HPE_JETDIRECT_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_HPE_JETDIRECT | no | Enable archive to disk for this specific source |
| SC4S_DEST_HPE_JETDIRECT_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=hpe:jetdirect")
```



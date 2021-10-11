# Vendor - HPE
## Product - Aruba devices


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| aruba:syslog | Dynamically  Created |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| aruba_ap     | netops          | none          |

### Filter type

Partial MSG Parse for BSD-style (non-CEF) messages: This filter parses message content for events that use the traditional aruba (BSD) message
format that have `program` values of `authmgr`, `sapd`, `stm`, or `wms`.  Additional `os:nix` logs for generic services such as `dnsmasq` will follow
the `os:nix` rules.

### Options


| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_ARUBA_AP_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_ARUBA_AP_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_ARUBA_AP| no | Enable archive to disk for this specific source |
| SC4S_DEST_ARUBA_AP_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=aruba:syslog")
```
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

Partial MSG Parse: This filter parses message content for events with a syslog "program" prefix "CPPM_". For complete parsing a dedicated port or
`vendor_product_by_source` entry must be added.


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
index=<asconfigured> (sourcetype=aruba:clearpass")
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

## Product - Procurve Switch

HP Procurve switches have multiple log formats used. 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Switch         | https://support.hpe.com/hpesc/public/docDisplay?docId=a00091844en_us | 
| Switch (A Series) (Flex) | https://techhub.hpe.com/eginfolib/networking/docs/switches/12500/5998-4870_nmm_cg/content/378584395.htm |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| hpe:procurve | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| hpe_procurve     | netops          | none          |

### Filter type

MSG Parse: This filter parses message content


### Options

Note listed for reference processing utilizes the Microsoft ArcSight log path as this format is a subtype of CEF

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_HPE_PROCURVE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_HPE_PROCURVE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_HPE_PROCURVE | no | Enable archive to disk for this specific source |
| SC4S_DEST_HPE_PROCURVE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=hpe:procurve")
```

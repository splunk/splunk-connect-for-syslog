# Vendor - Common Event Format Data Sources

## Product - Various products that send CEF-format messages via syslog

Each CEF product should have their own source entry in this documentation set.  In a departure
from normal configuration, all CEF products should use the "CEF" version of the unique port and
archive envrionmetn variable settings (rather than a unique one per product), as the CEF log path
handles all products sending events to SC4S in the CEF format. Examples of this include Arcsight,
Imperva, and Cyberark.  Therefore, the CEF environment varialbes for unique port, archive, etc.
should be set only _once_.

If your deployment has multiple CEF devices that send to more than one port,
set the CEF unique port variable(s) to just one of the ports in use.  Then, map the others with
container networking to the port chosen.  Example: If you have three CEF devices, sending on TCP
ports 2000,2001, and 2002, set `SC4S_LISTEN_CEF_TCP_PORT=2000`.  Then, map the other two with
container networking, e.g. `-p 2000:2000 -p 2001:2000 -p 2002:2000`.  This will route all
three ports to TCP port 2000 inside the container, and the single CEF log path will properly
process data from all three devices.

The source documentation included below is a reference baseline for any product that sends data
using the CEF log path.


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | https://bitbucket.org/SPLServices/ta-cef-for-splunk/downloads/                                                              |
| Product Manual | https://docs.imperva.com/bundle/cloud-application-security/page/more/log-configuration.htm                                                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

### Typical Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| Varies        | Varies                                                                                               |

### Typical Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Vendor_Product      | Varies      | main          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CEF_TLS_PORT      | empty string      | Enable a TLS  port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CEF | no | Enable archive to disk for this specific source |
| SC4S_DEST_CEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=cef source=<asconfigured>)
```

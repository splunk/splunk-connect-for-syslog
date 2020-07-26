# Vendor - Common Event Format Data Sources

## Product - Various products that send CEF-format messages via syslog

Each CEF product should have their own source entry in this documentation set.  In a departure
from normal configuration, all CEF products should use the "CEF" version of the unique port and
archive environment variable settings (rather than a unique one per product), as the CEF log path
handles all products sending events to SC4S in the CEF format. Examples of this include Arcsight,
Imperva, and Cyberark.  Therefore, the CEF environment variables for unique port, archive, etc.
should be set only _once_.

If your deployment has multiple CEF devices that send to more than one port,
set the CEF unique port variable(s) as a comma-separated list.  See [Unique Listening Ports](https://splunk-connect-for-syslog.readthedocs.io/en/develop/sources/#unique-listening-ports)
for details.

The source documentation included below is a reference baseline for any product that sends data
using the CEF log path.


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | https://bitbucket.org/SPLServices/ta-cef-for-splunk/downloads/                                                              |
| Product Manual | https://docs.imperva.com/bundle/cloud-application-security/page/more/log-configuration.htm                                                        |


### Splunk Metadat with CEF events

Splunk metadata for individual vendors that use the Common Event Format are governed by two or three of the initial columns
in the CEF string (following the leading `CEF:0` or "column 0").  These are `device_product`, `device_vendor`, and `device_event_class`.
The sc4s CEF parser first checks if a vendor is using the first two columns, and then (optionally) the fourth.
The third column, `device_version`, is not checked.  The parser assigns metadata according to the following csv files located in the
local context directory (typically `/opt/sc4s/local/context`):

* `common_event_format_source.csv`, which checks `device_product` and `device_vendor`, and
* `common_event_format_class.csv`, which additionally checks `device_event_class`.

If there is no matching row in either table corresponding to the values of these columns in the event, the default metadata below is
assigned.  If a new CEF source is encountered, additional rows can be added to either file to match the new CEF source so that
meaningful Splunk metadata can be assigned to the new source.

Here is a snippet of a sample Imperva CEF event:
```
Apr 19 10:29:53 3.3.3.3 CEF:0|Imperva Inc.|SecureSphere|12.0.0|Firewall|SSL Untraceable Connection|Medium|
```
and the corresponding match in `common_event_format_class.csv`:
```
Imperva Inc._SecureSphere_Firewall,sourcetype,imperva:waf:firewall:cef
```

* NOTE:  These files are installed when sc4s is first run, but will _not_ be overwritten by subsequent
sc4s installations.  Care should be taken to check the new "example" versions of these files for any new entries that have
been added to the files as part of the new release, and merge them appropriately with the production file(s).

### Default Sourcetype

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

### Default Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| Varies        | Varies                                                                                               |

### Default Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Vendor_Product      | Varies      | main          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_TLS_PORT      | empty string      | Enable a TLS  port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_CEF | no | Enable archive to disk for this specific source |
| SC4S_DEST_CEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=cef source=<asconfigured>)
```

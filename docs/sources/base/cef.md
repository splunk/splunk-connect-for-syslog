# Common Event Format (CEF)

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
| Splunk Add-on CEF | <https://bitbucket.org/SPLServices/ta-cef-for-splunk/downloads/>                                                              |
| Product Manual | <https://docs.imperva.com/bundle/cloud-application-security/page/more/log-configuration.htm>                                                        |

## Splunk Metadata with CEF events

The keys (first column) in `splunk_metadata.csv` for CEF data sources have a slightly different meaning than those for non-CEF ones.
The typical `vendor_product` syntax is instead replaced by checks against specific columns of the CEF event -- namely the first,
second, and fourth columns following the leading `CEF:0` ("column 0"). These specific columns refer to the CEF  `device_vendor`,
`device_product`, and `device_event_class`, respectively.  The third column, `device_version`, is not used for metadata assignment.

SC4S sets metadata based on the first two columns, and (optionally) the fourth.  While the key (first column) in the
`splunk_metadata` file for non-CEF sources uses a "vendor_product" syntax that is arbitrary, the syntax for this key for CEF
events is based on the actual contents of columns 1,2 and 4 from the CEF event, namely:

`device_vendor`\_`device_product`\_`device_class`

The final `device_class` portion is optional.  Therefore, CEF entries in `splunk_metadata` can have a key representing the vendor and
product, and others representing a vendor and product coupled with one or more additional classes.  This allows for more granular
metadata assignment (or overrides).

Here is a snippet of a sample Imperva CEF event that includes a CEF device class entry (which is "Firewall"):

```
Apr 19 10:29:53 3.3.3.3 CEF:0|Imperva Inc.|SecureSphere|12.0.0|Firewall|SSL Untraceable Connection|Medium|
```

and the corresponding match in `splunk_metadata.csv`:

```
Imperva Inc._SecureSphere_Firewall,sourcetype,imperva:waf:firewall:cef
```

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

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_TLS_PORT      | empty string      | Enable a TLS  port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_DEST_CEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |


# Log Extended Event Format (LEEF)

## Product - Various products that send LEEF V1 and V2 format messages via syslog

Each LEEF product should have their own source entry in this documentation set by vendor.  In a departure
from normal configuration, all LEEF products should use the "LEEF" version of the unique port and
archive environment variable settings (rather than a unique one per product), as the LEEF log path
handles all products sending events to SC4S in the LEEF format. Examples of this include QRadar itself
as well as other legacy systems.  Therefore, the LEEF environment variables for unique port, archive, etc.
should be set only _once_.

If your deployment has multiple LEEF devices that send to more than one port,
set the LEEF unique port variable(s) as a comma-separated list.  See [Unique Listening Ports](https://splunk-connect-for-syslog.readthedocs.io/en/develop/sources/#unique-listening-ports)
for details.

The source documentation included below is a reference baseline for any product that sends data
using the LEEF log path.

Some vendors implement LEEF v2.0 format events incorrectly, omitting the required "key=value" separator field
from the LEEF header, thus forcing the consumer to assume the default tab `\t` character.
SC4S will correctly process this omission, but will not correctly process other non-compliant formats.

The LEEF format allows for the inclusion of a field `devTime` containing the device timestamp and allows the sender to
also specify the format of this timestamp in another field called `devTimeFormat`, which uses the Java Time format.
SC4S uses syslog-ng strptime format which is not directly translatable to the Java Time format. Therefore, SC4S has
provided support for the following common formats.  If needed, additional time formats can be requested via an issue on
github.

```
    '%s.%f',
    '%s',
    '%b %d %H:%M:%S.%f',
    '%b %d %H:%M:%S',
    '%b %d %Y %H:%M:%S.%f',
    '%b %e %Y %H:%M:%S',
    '%b %e %H:%M:%S.%f',
    '%b %e %H:%M:%S',
    '%b %e %Y %H:%M:%S.%f',
    '%b %e %Y %H:%M:%S'  
```

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on LEEF | None                                                          |
| Product Manual | <https://www.ibm.com/support/knowledgecenter/SS42VS_DSM/com.ibm.dsm.doc/c_LEEF_Format_Guide_intro.html>                                                 |

## Splunk Metadata with LEEF events

The keys (first column) in `splunk_metadata.csv` for LEEF data sources have a slightly different meaning than those for non-LEEF ones.
The typical `vendor_product` syntax is instead replaced by checks against specific columns of the LEEF event -- namely the first and
second, columns following the leading `LEEF:VERSION` ("column 0"). These specific columns refer to the LEEF  `device_vendor`,
and `device_product`, respectively.

`device_vendor`\_`device_product`

Here is a snippet of a sample LANCOPE event in LEEF 2.0 format:

```
<111>Apr 19 10:29:53 3.3.3.3 LEEF:2.0|Lancope|StealthWatch|1.0|41|^|src=192.0.2.0^dst=172.50.123.1^sev=5^cat=anomaly^srcPort=81^dstPort=21^usrName=joe.black
```

and the corresponding match in `splunk_metadata.csv`:

```
Lancope_StealthWatch,source,lancope:stealthwatch
```

### Default Sourcetype

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| LEEF:1         | Common sourcetype for all LEEF v1 events                                                               |
| LEEF:2:`<separator>`         | Common sourcetype for all LEEF v2 events `separator` is the printable literal or hex value of the separator used in the event |

### Default Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| `vendor`:`product`        | Varies                                                                                               |

### Default Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Vendor_Product      | Varies      | main          | none          |

### Filter type

MSG Parse: This filter parses message content

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_LEEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_LEEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_LEEF_TLS_PORT      | empty string      | Enable a TLS  port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_DEST_LEEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

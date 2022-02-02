
# SC4S Destination Configuration

Splunk Connect for Syslog can be configured to utilize any destination available in
syslog-ng OSE. The configuration system provides ease of use helpers to manage configuration
for the three most common destination needs, Splunk HEC, RFC5424 Syslog, and Legacy BSD Syslog.

In the getting started guide you configured the Splunk HEC "DEFAULT" destination to receive all traffic by default. The "DEFAULT" destination should be configured to accept all events to ensure that at least one
destination has the event to avoid data loss due to misconfiguration. The following example demonstrates configuration of a second HEC destination where only "selected" data will be sent.

## Example 1 Send all events
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=GLOBAL
```

## Example 2 Send only cisco IOS Events 
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=SELECT
SC4S_DEST_CISCO_IOS_ALTERNATES=d_fmt_hec_OTHER
```

## Example 3 Send only cisco IOS events that are not debug
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=SELECT
```

```c
#filename:
application sc4s-lp-cisco_ios_dest_fmt_other{{ source }}[sc4s-lp-dest-select-d_fmt_hec_OTHER] {
    filter {
        match('CISCO_IOS' value('.dest_key'))
        #Match any cisco event that is not like "%ACL-7-1234"
        and not message('^%[^\-]+-7-');
    };    
};

```

# Supported Simple Destination configurations

SC4S Supports the following destination configurations via configuration. Any custom destination
can be supported (defined by syslog-ng OSE)

* Splunk HTTP Event Collector (HEC)
* RFC5424 format without frames i.e. ```<166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID: ```
* RFC5424 format with frames also known as RFC6587 ```123 <166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID: ```
* RFC3194 (BSD format) ```<134>Feb  2 13:43:05.000 horse-ammonia CheckPoint[26203]:```

## HEC Destination Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_<ID>_URL | url | URL(s) of the Splunk endpoint, can be a single URL space separated list |
| SC4S_DEST_SPLUNK_HEC_<ID>_TOKEN | string | Splunk HTTP Event Collector Token |
| SC4S_DEST_SPLUNK_HEC_<ID>_MODE | string | "GLOBAL" or "SELECT" |
| SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY | yes(default) or no | verify HTTP(s) certificate |

## Syslog Standard destination.

Note: in many cases destinations incorrectly assert "syslog" support. IETF standards RFC5424, RFC5425, RFC6587 define the use of "syslog" as a network protocol. Often the actual configuration required is Legacy BSD syslog which is NOT a standard and was documented "historically" in RFC3194 see BSD Destination section.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SYSLOG_<ID>_HOST | fqdn or ip | the FQDN or IP of the target |
| SC4S_DEST_SYSLOG_<ID>_PORT | number | 601 (default when framed) 514 (default when not framed) |
| SC4S_DEST_SYSLOG_<ID>_IETF | yes,no | default "yes" use IETF Standard frames |
| SC4S_DEST_SYSLOG_<ID>_MODE | string | "GLOBAL" or "SELECT" |

## BSD legacy destination (Non standard)

Note: in many cases destinations incorrectly assert "syslog" support. IETF standards RFC5424, RFC5425, RFC6587 define the use of "syslog" as a network protocol. Often the actual configuration required is Legacy BSD syslog which is NOT a standard and was documented "historically" in RFC3194 see BSD Destination section.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_BSD_<ID>_HOST | fqdn or ip | the FQDN or IP of the target |
| SC4S_DEST_BSD_<ID>_PORT | number | default 514 |
| SC4S_DEST_BSD_<ID>_TRANSPORT | tcp,udp,tls | default tcp |
| SC4S_DEST_BSD_<ID>_MODE | string | "GLOBAL" or "SELECT" |


## Configuration of Alternate Destinations

In addition to the standard HEC destination that is used to send events to Splunk, alternate destinations can be created and configured
in SC4S.  All alternate destinations (including alternate HEC destinations discussed below) are configured using the environment
variables below.  Global and/or source-specific forms of the variables below can be used to send data to additional and/or alternate
destinations.

* NOTE:  The administrator is responsible for ensuring that any non-HEC alternate destinations are configured in the
local mount tree, and that the underlying syslog-ng process in SC4S properly parses them.

* NOTE:  Do not include the primary HEC destination (`d_fmt_hec`) in any list of alternate destinations.  The configuration of the primary HEC
destination is configured separately from that of the alternates below.  However, _alternate_ HEC destinations (e.g. `d_fmt_hec_FOO`) should be
configured below, just like any other user-supplied destination.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_ALTERNATES | Comma or space-separated list of syslog-ng destinations  | Send specific sources to alternate syslog-ng destinations using the VENDOR_PRODUCT syntax, e.g. `SC4S_DEST_CISCO_ASA_ALTERNATES=d_syslog_foo`  |

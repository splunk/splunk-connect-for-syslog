
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
application sc4s-lp-cisco_ios_dest_fmt_other{{ source }}[sc4s-lp-dest-select-d_fmt_hec_other] {
    filter {
        'CISCO_IOS' eq "${fields.sc4s_vendor}_${fields.sc4s_product}"
        #Match any cisco event that is not like "%ACL-7-1234"
        and not message('^%[^\-]+-7-');
    };    
};

```

## Example 4 Mcafee EPO send RFC5424 events without frames to third party system

Note in most cases when a destination requires syslog the requirement is referring to
legacy BSD syslog (RFC3194) not standard syslog RFC5424

The destination name is taken from the env var each destination must have a unique name regardless of type.
This value should be short and meaningful. 

```bash
#env_file
SC4S_DEST_SYSLOG_MYSYS_HOST=172.17.0.1
SC4S_DEST_SYSLOG_MYSYS_PORT=514
SC4S_DEST_SYSLOG_MYSYS_MODE=SELECT
# set to #yes for ietf frames
SC4S_DEST_SYSLOG_MYSYS_IETF=no 
```

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-mcafee_epo_d_syslog_msys.conf
application sc4s-lp-mcafee_epo_d_syslog_msys[sc4s-lp-dest-select-d_syslog_msys] {
    filter {
        'mcafee' eq "${fields.sc4s_vendor}"
        and 'epo' eq "${fields.sc4s_product}"
    };    
};
```

## Example 5 Cisco ASA send to a third party SIEM

The destination name is taken from the env var each destination must have a unique name regardless of type.
This value should be short and meaningful

In most cases when a third party system needs "syslog" the requirement is to send "legacy BSD" as follows
This is often refereed to as RFC3194 

```bash
#env_file
SC4S_DEST_BSD_OLDSIEM_HOST=172.17.0.1
SC4S_DEST_BSD_OLDSIEM_PORT=514
SC4S_DEST_BSD_OLDSIEM_MODE=SELECT
# set to #yes for ietf frames
```

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-mcafee_epo_d_bsd_oldsiem.conf
application sc4s-lp-mcafee_epo_d_bsd_oldsiem[sc4s-lp-dest-select-d_bsd_oldsiem] {
    filter {
        'mcafee' eq "${fields.sc4s_vendor}"
        and 'epo' eq "${fields.sc4s_product}"
    };    
};
```

## Example 6 Mcafee EPO send RFC5424 events without frames to third party system

The destination name is taken from the env var each destination must have a unique name regardless of type.
This value should be short and meaningful

```bash
#env_file
SC4S_DEST_SYSLOG_MYSYS_HOST=172.17.0.1
SC4S_DEST_SYSLOG_MYSYS_PORT=514
SC4S_DEST_SYSLOG_MYSYS_MODE=SELECT
# set to #yes for ietf frames
SC4S_DEST_SYSLOG_MYSYS_IETF=no 
```

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-mcafee_epo_d_syslog_msys.conf
application sc4s-lp-mcafee_epo_d_syslog_msys[sc4s-lp-dest-select-d_syslog_msys] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}"
        and 'asa' eq "${fields.sc4s_product}"
    };    
};
```

# Supported Simple Destination configurations

SC4S Supports the following destination configurations via configuration. Any custom destination
can be supported (defined by syslog-ng OSE)

* Splunk HTTP Event Collector (HEC)
* RFC5424 format without frames i.e. ```<166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID: ```
* RFC5424 format with frames also known as RFC6587 ```123 <166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID: ```
* RFC3164 (BSD format) ```<134>Feb  2 13:43:05.000 horse-ammonia CheckPoint[26203]:```

## HEC Destination Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_URL | url | URL(s) of the Splunk endpoint, can be a single URL space separated list |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_TOKEN | string | Splunk HTTP Event Collector Token |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT" |
| SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY | yes(default) or no | verify HTTP(s) certificate |

### HTTP Compression

HTTP traffic compression allows reducing the network connection bandwidth congestion, enabling the transmission of a larger volume of logs using the same bandwidth.\
The currently supported version of `syslog-ng` offers two out of four compression algorithms from the `curl` library: `deflate` and `gzip`. Compression relies on the `zlib` library. Utilizing compression may result in lower CPU load and increased utilization of RAM. Compression affects the content but not the HTTP headers. Enabling batch packet processing will make the solution particularly efficient as it allows for compressing a larger number of logs at once.\

| Variable                                           | Values/Default   | Description |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_COMPRESSION_METHOD;       | None(default) | Disable HTTP compression  |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_COMPRESSION_METHOD;       | deflate |   |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_COMPRESSION_METHOD;       | gzip |   |

## Syslog Standard destination.

Note: in many cases destinations incorrectly assert "syslog" support. IETF standards RFC5424, RFC5425, RFC6587 define the use of "syslog" as a network protocol. Often the actual configuration required is Legacy BSD syslog which is NOT a standard and was documented "historically" in RFC3164 see BSD Destination section.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SYSLOG_&lt;ID&gt;_HOST | fqdn or ip | the FQDN or IP of the target |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_PORT | number | 601 (default when framed) 514 (default when not framed) |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_IETF | yes,no | default "yes" use IETF Standard frames |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_TRANSPORT | tcp,udp,tls | default tcp |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT" |

## BSD legacy destination (Non standard)

Note: in many cases destinations incorrectly assert "syslog" support. IETF standards RFC5424, RFC5425, RFC6587 define the use of "syslog" as a network protocol. Often the actual configuration required is Legacy BSD syslog which is NOT a standard and was documented "historically" in RFC3164 see BSD Destination section.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_BSD_&lt;ID&gt;_HOST | fqdn or ip | the FQDN or IP of the target |
| SC4S_DEST_BSD_&lt;ID&gt;_PORT | number | default 514 |
| SC4S_DEST_BSD_&lt;ID&gt;_TRANSPORT | tcp,udp,tls | default tcp |
| SC4S_DEST_BSD_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT" |

## Configuration of Filtered Alternate Destinations (Advanced)

Though source-specific forms of the variables configured above will limit configured alternate destinations to a specific data source, there
are cases where even more granularity is desired within a specific data source (e.g. to send all Cisco ASA "debug" traffic to Cisco Prime for
analysis).  This extra traffic may or may not be needed in Splunk.  To accommodate this use case, Filtered Alternate Destinations allow a
filter to be supplied to redirect a _portion_ of a given source's traffic to a list of alternate destinations (and, optionally, to prevent
matching events from being sent to Splunk).  Again, these are configured through environment variables similar
to the ones above:

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_ALT_FILTER | syslog-ng filter | Filter to determine which events are sent to alternate destination(s) |
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_FILTERED_ALTERNATES | Comma or space-separated list of syslog-ng destinations  | Send filtered events to alternate syslog-ng destinations using the VENDOR_PRODUCT syntax, e.g. `SC4S_DEST_CISCO_ASA_FILTERED_ALTERNATES`  |

* NOTE:  This is an advanced capability, and filters and destinations using proper syslog-ng syntax must be constructed prior to utilizing
this feature.

* NOTE:  Unlike the standard alternate destinations configured above, the regular "mainline" destinations (including the primary HEC
destination or configured archive destination (`d_hec` or `d_archive`)) are _not_ included for events matching the configured alternate
destination filter.  If an event matches the filter, the list of filtered alternate destinations completely replaces any mainline destinations
including defaults and global or source-based standard alternate destinations.  Be sure to include them in the filtered destination list if
desired.

* HINT:  Since the filtered alternate destinations completely replace the mainline destinations (including HEC to Splunk), a filter that
matches all traffic can be used with a destination list that does _not_ include the standard HEC destination to effectively turn off HEC
for a given data source.
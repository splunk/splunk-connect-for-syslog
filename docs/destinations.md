
# Configure SC4S destinations

You can configure Splunk Connect for Syslog to use any destination available in
syslog-ng OSE. Helpers manage configuration
for the three most common destination needs: Splunk HEC, RFC5424 Syslog, and Legacy BSD Syslog.

Configure the default destination to accept all events. This ensures that at least one destination has the event and helps to avoid data loss due to misconfiguration. The following example demonstrates configuration of a second HEC destination where only selected data will be sent.

## Example 1: Send all events
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=GLOBAL
```

## Example 2: Send only Cisco IOS events 
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=SELECT
SC4S_DEST_CISCO_IOS_ALTERNATES=d_fmt_hec_OTHER
```

## Example 3: Send only Cisco IOS events that are not debugged
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

## Example 4: McAfee EPO sends RFC5424 events without frames to a third party system

In most cases when a destination requires syslog, the requirement is referring to
legacy BSD syslog (RFC3194), not standard syslog RFC5424

The destination name is taken from the environment variable. Each destination must have a unique name regardless of type. This value should be short and meaningful. 

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

## Example 5: Cisco ASA sends to a third party SIEM

The destination name is taken from the environment variable, each destination must have a unique name regardless of type. This value should be short and meaningful.

In most cases when a third party system requires syslog, it is to send legacy BSD,
this is often refereed to as RFC3194:

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

## Example 6: McAfee EPO sends RFC5424 events without frames to third party system

The destination name is taken from the environment variable, each destination must have a unique name regardless of type. This value should be short and meaningful.

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

# Supported simple destination configurations

SC4S supports the following destination configurations. Any custom destination
can be supported as defined by syslog-ng OSE:

* Splunk HTTP Event Collector (HEC).
* RFC5424 format without frames, for example, ```<166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID: ```
* RFC5424 format with frames, also known as RFC6587 ```123 <166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID: ```
* RFC3164 (BSD format) ```<134>Feb  2 13:43:05.000 horse-ammonia CheckPoint[26203]:```

## HEC destination configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_URL | url | URL of the Splunk endpoint, this can be a single URL or a space-separated list. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_TOKEN | string | Splunk HTTP Event Collector token. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT". |
| SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY | yes(default) or no | Verify HTTP(s) certificates |

### HTTP Compression

HTTP traffic compression helps to reduce network bandwidth usage. SC4S currently supports gzip for compressing transmitted traffic.

Using the gzip compression algorithm can result in lower CPU load and increased utilization of RAM. The algorithm may also cause a decrease in performance by 6% to 7%.

Compression affects the content but does not affect the HTTP headers. Enable batch packet processing to make the solution efficient, as this allows compression of a large number of logs at once.


| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_HTTP_COMPRESSION;       | yes or no(default) | Compress outgoing HTTP traffic using the gzip method. |


## Syslog standard destination

In many cases, destinations incorrectly assert syslog support. Internet Engineering Task Force standards RFC5424, RFC5425, and RFC6587 define the use of "syslog" as a network protocol. Often the actual configuration required is Legacy BSD syslog which is not a standard and was documented in RFC3164.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SYSLOG_&lt;ID&gt;_HOST | fqdn or ip | The FQDN or IP of the target. |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_PORT | number | 601 is the default when framed, 514 is the default when not framed). |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_IETF | yes/no, the default value is yes. | Use IETF Standard frames. |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_TRANSPORT | tcp,udp,tls. The default value is tcp. |  |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT". |

## BSD legacy destination (Non standard)

In many cases, destinations incorrectly assert syslog support. Internet Engineering Task Force standards RFC5424, RFC5425, and RFC6587 define the use of syslog as a network protocol. Often the actual configuration required is Legacy BSD syslog which is not a standard and was documented in RFC3164.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_BSD_&lt;ID&gt;_HOST | fqdn or ip | The FQDN or IP of the target. |
| SC4S_DEST_BSD_&lt;ID&gt;_PORT | number, the default is 514. |  |
| SC4S_DEST_BSD_&lt;ID&gt;_TRANSPORT | tcp,udp,tls, the default is tcp. |  |
| SC4S_DEST_BSD_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT". |

## Advanced topic: Configure filtered alternate destinations 

Though source-specific forms of the variables configured in this topic will limit configured alternate destinations to a specific data source, you may require more granularity for a specific data source. For example, you may want to send all Cisco ASA debug traffic to Cisco Prime for
analysis. To accommodate this, filtered alternate destinations let you supply a
filter to redirect a portion of a source's traffic to a list of alternate destinations and, optionally, prevent
matching events from being sent to Splunk. These are configured through environment variables:

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_ALT_FILTER | syslog-ng filter | Filter to determine which events are sent to alternate destinations. |
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_FILTERED_ALTERNATES | Comma or space-separated list of syslog-ng destinations.  | Send filtered events to alternate syslog-ng destinations using the VENDOR_PRODUCT syntax, for example, `SC4S_DEST_CISCO_ASA_FILTERED_ALTERNATES`.  |

This is an advanced capability, and filters and destinations using proper syslog-ng syntax must be constructed before using this functionality.

The regular destinations, including the primary HEC
destination or configured archive destination, for example `d_hec` or `d_archive`, are not included for events matching the configured alternate
destination filter. If an event matches the filter, the list of filtered alternate destinations completely replaces any mainline destinations,
including defaults and global or source-based standard alternate destinations. Include them in the filtered destination list if
desired.

Since the filtered alternate destinations completely replace the mainline destinations, including HEC to Splunk, a filter that
matches all traffic can be used with a destination list that does not include the standard HEC destination to effectively turn off HEC
for a given data source.

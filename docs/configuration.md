# SC4S configuration variables

SC4S is primarily controlled by environment variables. This topic describes the categories and variables you need to properly configure SC4S for your environment.

## Global configuration variables

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_USE_REVERSE_DNS | yes or no (default) | Use reverse DNS to identify hosts when HOST is not valid in the syslog header. |
| SC4S_REVERSE_DNS_KEEP_FQDN | yes or no (default) | When enabled, SC4S will not extract the hostname from FQDN, and instead will pass the full domain name to the host. |
| SC4S_CONTAINER_HOST | string | Variable that is passed to the container to identify the actual log host for container implementations. |

If the host value is not present in an event, and you require that a true hostname be attached to each event, SC4S provides an optional ability to perform a reverse IP to name lookup. If the variable `SC4S_USE_REVERSE_DNS` is set to "yes", then SC4S first checks `host.csv` and replaces the value of `host` with the specified value that matches the incoming IP address. If no value is found in `host.csv`, SC4S attempts a reverse DNS lookup against the configured nameserver. In this case, SC4S by default extracts only the hostname from FQDN (`example.domain.com` -> `example`). If `SC4S_REVERSE_DNS_KEEP_FQDN` variable is set to "yes", full domain name is assigned to the host field.

**Note:** Using the `SC4S_USE_REVERSE_DNS` variable can have a significant impact on performance if the reverse DNS facility is not performant. Check this variable if you notice that events are indexed later than the actual timestamp
in the event, for example, if you notice a latency between `_indextime` and `_time`.

## Configure your external HTTP proxy

Many HTTP proxies are not provisioned with application traffic in mind. Ensure adequate capacity is available to avoid data loss and proxy outages. The following variables must be entered in lower case:


| Variable | Values        | Description |
|----------|---------------|-------------|
| http_proxy | undefined | Use libcurl format proxy string "http://username:password@proxy.server:port" |
| https_proxy | undefined | Use libcurl format proxy string "http://username:password@proxy.server:port" |

## Configure your Splunk HEC destination 

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_CIPHER_SUITE | comma separated list | Opens the SSL cipher suite list. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_SSL_VERSION |  comma separated list | Opens the SSL version list. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_WORKERS | numeric | The number of destination workers (threads), the default value is 10 threads. You do not need to change this variable from the default unless your environment has a very high or low volume. Consult with the SC4S community for advice about configuring your settings for environments with very high or low volumes. |
| SC4S_DEST_SPLUNK_INDEXED_FIELDS | r_unixtime,facility,<br>severity,<br>container,<br>loghost,<br>destport,<br>fromhostip,<br>proto<br><br>none | This is the list of SC4S indexed fields that will be included with each event in Splunk. The default is the entire list except "none". Two other indexed fields, `sc4s_vendor_product` and `sc4s_syslog_format`, also appear along with the fields selected and cannot be turned on or off individually. If you do not want any indexed fields, set the value to the single value of "none". When you set this variable, you must separate multiple entries with commas, do not include extra spaces.<br></br>This list maps to the following indexed fields that will appear in all Splunk events:<br>facility: sc4s_syslog_facility<br>severity: sc4s_syslog_severity<br>container: sc4s_container<br>loghost: sc4s_loghost<br>dport: sc4s_destport<br>fromhostip: sc4s_fromhostip<br>proto: sc4s_proto|

The destination operating parameters outlined above should be individually controlled using the destination ID. For example, to set the number of workers for the default destination, use `SC4S_DEST_SPLUNK_HEC_DEFAULT_WORKERS`. To configure workers for the alternate HEC destination `d_hec_FOO`, use `SC4S_DEST_SPLUNK_HEC_FOO_WORKERS`.

## Configure timezones for legacy sources

Set the `SC4S_DEFAULT_TIMEZONE` variable to a recognized "zone info" (Region/City) time zone format such as `America/New_York`.
Setting this value forces SC4S to use the specified timezone and honor its associated Daylight Savings rules for all events without a timezone offset in the header or message payload.

## Configure your SC4S disk buffer 

SC4S provides the ability to minimize the number of lost events if the connection to all the Splunk indexers is lost. 
This capability utilizes the disk buffering feature of Syslog-ng. 

SC4S receives a response from the Splunk HTTP Event
Collector (HEC) when a message is received successfully. If a confirmation message from the HEC endpoint is not
received (or a “server busy” reply, such as a “503” is sent), the load balancer will try the next HEC endpoint in the pool.
If all pool members are exhausted, for example, if there were a full network outage to the HEC endpoints, events
will queue to the local disk buffer on the SC4S Linux host.

SC4S will continue attempting to send the failed
events while it buffers all new incoming events to disk. If the disk space allocated to disk buffering fills up then SC4S
will stop accepting new events and subsequent events will be lost.

Once SC4S gets confirmation that events are again being
received by one or more indexers, events will then stream from the buffer using FIFO queueing.

The number of events in the disk buffer will reduce as long as the incoming event volume is less than the maximum SC4S, with the disk
buffer in the path, can handle. When all events have been emptied from the disk buffer, SC4S will resume streaming events
directly to Splunk.

Disk buffers in SC4S are allocated per destination.  Keep this in mind when using additional destinations that have disk buffering configured. By default, when you configure alternate HEC destinations, disk buffering is configured identically to that of the main HEC destination, unless overridden individually.

### Estimate your storage allocation
* Start with your estimated maximum events per second that each SC4S server will experience. Based on the maximum
throughput of SC4S with disk buffering enabled, the conservative estimate for maximum events per second would be 60K. You should use the maximum rate in your environment for this calculation, not the maximum rate that SC4S can handle.
* Estimate you average event size based on your data sources. It is common industry practice to estimate log events as 800 bytes on average. 
* Factor in the maximum length of connectivity downtime you want disk buffering to be able to handle. This value depends on your risk tolerance.
* syslog-ng imposes significant overhead to maintain its internal data structures so that the data can be properly "played back" upon network restoration. This overhead currently runs at about 1.7x above the total storage size for the raw messages themselves, and can be higher for "fallback" data sources due to the overlap of syslog-ng
data fields containing some or all of the original message.

As an example, to protect against a full day of lost connectivity from SC4S to all your indexers at maximum throughput, the
calculation would look like the following:

60,000 EPS * 86400 seconds * 800 bytes * 1.7 = 6.4 TB of storage

### About disk buffering
Note the following about disk buffering:

* "Reliable" disk buffering offers little advantage over "normal" disk buffering, but has a significant performance penalty.
For this reason, normal disk buffering is recommended.

* Pay attention to the cumulative buffer requirements when allocating local disk space.

* Disk buffer storage is configured using container volumes and is persistent between container restarts.
Be sure to account for disk space requirements on the local SC4S host when you create the container volumes in your respective
runtime environment. These volumes can grow significantly during
an extended outage to the SC4S destination HEC endpoints. See the ["Estimate your storage allocation"](#estimate-your-storage-allocation) section.

* When you change the disk buffering directory, the new directory must exist. Otherwise, syslog-ng will fail to start.

* When you change the disk buffering directory, if buffering has previously occurred on that instance, a persist file may exist which will prevent syslog-ng from changing the directory.

### Disk Buffer Variables

| Variable                                           | Values/Default   | Description |
|----------------------------------------------------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE       | yes(default) or no | Enable local disk buffering.  |
| SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE     | yes or no(default) | Enable reliable/normal disk buffering (normal is the recommended value).|
| SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE   | bytes (10241024) | The worker's memory buffer size in bytes, used with reliable disk buffering.|
| SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH |messages (15000) | The worker's memory buffer size in message count, used with normal disk buffering.|
| SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE  | bytes (53687091200) | Size of local disk buffering bytes, the default is 50 GB per worker.|
| SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DIR          | path | Location to store the disk buffer files. This location is fixed when using the container and should not be modified.  |

**Note:** The buffer options apply to each worker rather than the
entire destination.

## Archive File Configuration

This feature is designed to support compliance or diode mode archival of all messages. The files are stored in a folder
structure at the mount point using the pattern shown in the table below, depending on the value of the `SC4S_GLOBAL_ARCHIVE_MODE` variable.
Events for both modes are formatted using syslog-ng's EWMM template.

| Variable | Value/Default    | Location/Pattern |
|----------|------------------|------------------|
| SC4S_GLOBAL_ARCHIVE_MODE | compliance(default) | ``<archive mount>/${.splunk.sourcetype}/${HOST}/$YEAR-$MONTH-$DAY-archive.log`` |
| SC4S_GLOBAL_ARCHIVE_MODE | diode | ``<archive mount>/${YEAR}/${MONTH}/${DAY}/${fields.sc4s_vendor_product}_${YEAR}${MONTH}${DAY}${HOUR}${MIN}.log"`` |

Use the following variables to select global archiving or per-source archiving. SC4S does not prune the files that are created,
therefore an administrator must provide a means of log rotation to prune files and move them to an archival system to avoid exhausting disk space.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_ARCHIVE_GLOBAL | yes or undefined | Enable archiving of all vendor_products. |
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_ARCHIVE | yes(default) or undefined | Enables selective archiving by vendor product. |

## Syslog Source Configuration

| Variable | Values/Default     | Description |
|----------|--------------------|-------------|
| SC4S_SOURCE_TLS_ENABLE | yes or no(default) | Enable TLS globally.  Be sure to configure the certificate as shown below. |
| SC4S_LISTEN_DEFAULT_TLS_PORT | undefined or 6514  | Enable a TLS listener on port 6514. |
| SC4S_LISTEN_DEFAULT_RFC6425_PORT | undefined or 5425  | Enable a TLS listener on port 5425. |
| SC4S_SOURCE_TLS_OPTIONS | `no-sslv2`         | Comma-separated list of the following options: `no-sslv2, no-sslv3, no-tlsv1, no-tlsv11, no-tlsv12, none`.  See syslog-ng docs for the latest list and default values. |
| SC4S_SOURCE_TLS_CIPHER_SUITE | See openssl        | Colon-delimited list of ciphers to support, for example, `ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384`.  See openssl for the latest list and defaults. |
| SC4S_SOURCE_TCP_MAX_CONNECTIONS | 2000               | Maximum number of TCP connections. |
| SC4S_SOURCE_UDP_IW_USE | yes or no(default)           | Determine whether to change the initial Window size for UDP. |
| SC4S_SOURCE_UDP_FETCH_LIMIT | 1000               | Number of events to fetch from server buffer at one time. |
| SC4S_SOURCE_UDP_IW_SIZE | 250000             | Initial Window size.|
| SC4S_SOURCE_TCP_IW_SIZE | 20000000           | Initial Window size. |
| SC4S_SOURCE_TCP_FETCH_LIMIT | 2000           | Number of events to fetch from server buffer at one time.|
| SC4S_SOURCE_UDP_SO_RCVBUFF | 17039360           | Server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_TCP_SO_RCVBUFF | 17039360           | Server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_TLS_SO_RCVBUFF | 17039360           | Server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_RFC5426_SO_RCVBUFF | 17039360           | Server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_RFC6587_SO_RCVBUFF | 17039360           | Server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_RFC5425_SO_RCVBUFF | 17039360           | Server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_LISTEN_UDP_SOCKETS | 4                  | Number of kernel sockets per active UDP port, which configures multi-threading of the UDP input buffer in the kernel to prevent packet loss. Total UDP input buffer is the multiple of SOCKETS x SO_RCVBUFF. |
| SC4S_SOURCE_LISTEN_RFC5426_SOCKETS | 1                  | Number of kernel sockets per active UDP port, which configures multi-threading of the input buffer in the kernel to prevent packet loss. Total UDP input buffer is the sum of SOCKETS x SO_RCVBUFF. |
| SC4S_SOURCE_LISTEN_RFC6587_SOCKETS | 1                  | Number of kernel sockets per active UDP port, which configures multi-threading of the input buffer in the kernel to prevent packet loss. Total UDP input buffer is the sum of SOCKETS x SO_RCVBUFF. |
| SC4S_SOURCE_LISTEN_RFC5425_SOCKETS | 1                  | Number of kernel sockets per active UDP port, which configures multi-threading of the input buffer in the kernel to prevent packet loss. Total UDP input buffer is the sum of SOCKETS x SO_RCVBUFF. |
| SC4S_SOURCE_STORE_RAWMSG | undefined or "no"  | Store unprocessed "on the wire" raw message in the RAWMSG macro for use with the "fallback" sourcetype. Do not set this in production, substantial memory and disk overhead will result. Use this only for log path and filter development. |
| SC4S_IPV6_ENABLE | yes or no(default) | Enable dual-stack IPv6 listeners and health checks. |

## Configure your syslog source TLS certificate 

1. Create the folder ``/opt/sc4s/tls`` .
2. Uncomment the appropriate mount line in the unit or yaml file.
3. Save the server private key in PEM format with no password to ``/opt/sc4s/tls/server.key``.
4. Save the server certificate in PEM format to ``/opt/sc4s/tls/server.pem``.
5. Ensure the entry `SC4S_SOURCE_TLS_ENABLE=yes` exists in ``/opt/sc4s/env_file``.

### Configure additional PKI trust anchors

Additional certificate authorities may be trusted by appending each PEM formatted certificate to `/opt/sc4s/tls/trusted.pem`.

## Configure SC4S metadata 

### Override the log path of indexes or metadata

Set Splunk metadata before the data arrives in Splunk and before any add-on processing occurs. The filters apply the index, source, sourcetype, host, and timestamp metadata automatically by
individual data source. Values for this metadata, including a recommended index and output format, are
included with all "out-of-the-box" log paths included with SC4S and are chosen to properly interface with the corresponding
add-on in Splunk. You must ensure all recommended indexes accept this data if the defaults
are not changed.

To accommodate the override of default values, each log path consults
an internal lookup file that maps Splunk metadata to the specific data source being processed. This file contains the
defaults that are used by SC4S to set the appropriate Splunk metadata, `index`, `host`, `source`, and `sourcetype`, for each
data source. This file is not directly available to the administrator, but a copy of the file is deposited in the local mounted directory
for reference, `/opt/sc4s/local/context/splunk_metadata.csv.example` by default. This copy is provided solely for reference. To add to the list or to override default entries, create an override file without
the `example` extension (for example `/opt/sc4s/local/context/splunk_metadata.csv`) and modify it according to the instructions below.

`splunk_metadata.csv` is a CSV
file containing a "key" that is referenced in the log path for each data source. These keys are documented in the individual
source files in this section, and let you override Splunk metadata. 

The following is example line from a typical `splunk_metadata.csv` override file:

```bash
juniper_netscreen,index,ns_index
```

The columns in this file are `key`, `metadata`, and `value`. To make a change using the override file, consult the `example` file (or
the source documentation) for the proper key and modify and add rows in the table, specifying one or
more of the following `metadata/value` pairs for a given `key`:

   * `key` which refers to the vendor and product name of the data source, using the `vendor_product` convention. For overrides, these keys
   are listed in the `example` file. For new custom sources, be sure to choose a key that accurately reflects the vendor and product
   being configured and that matches the log path.
   * `index` to specify an alternate `value` for index.
   * `source` to specify an alternate `value` for source.
   * `host` to specify an alternate `value` for host.
   * `sourcetype` to specify an alternate `value` for sourcetype. Only change this if no upstream
    TA used, or a custom TA is being used.
   * `sc4s_template` to specify an alternate `value` for the syslog-ng template that will be used to format the event that is
   indexed by Splunk. Changing this will affect the upstream TA. The template
   choices are documented [here](configuration.md#splunk-connect-for-syslog-output-templates-syslog-ng-templates).

In our example above, the `juniper_netscreen` key references a new index used for that data source called `ns_index`.

For most deployments the index should be the only change needed, other default metadata should almost
never be overridden. 

The `splunk_metadata.csv` file is a true override file and the entire `example` file should not be copied over to the
override. The override file is usually just one or two lines, unless an entire index category (for example `netfw`) needs to be overridden.

When building a custom
SC4S log path, append the `splunk_metadata.csv` file with an appropriate new key and default for the index. The new key will not exist in the internal lookup or in the `example` file.  Care should be taken during log path design to
choose appropriate index, sourcetype and template defaults so that admins are not compelled to override them.  If the custom log path is later
added to the list of SC4S-supported sources, this addendum can be removed.

The `splunk_metadata.csv.example` file is provided for reference only and is not used directly by SC4S. It is an exact copy of the internal file, and can therefore change from release to release. Be sure to check the example file to make
sure the keys for any overrides map correctly to the ones in the example file.

### Override index or metadata based on host, ip, or subnet (compliance overrides)

In some cases you can provide the same overrides based on PCI scope, geography, or other criteria. Use a file that uniquely identifies these source exceptions via syslog-ng filters,
which map to an associated lookup of alternate indexes, sources, or other metadata. Indexed fields can also be
added to further classify the data.

* The `conf` and `csv` files referenced below are populated into the `/opt/sc4s/local/context` directory when SC4S is run for the first
time, in a similar fashion to `splunk_metadata.csv`.
After this first-time population of the files takes place, you can edit them and restart SC4S for the changes to take effect. To get started:

* Edit the file ``compliance_meta_by_source.conf`` to supply uniquely named filters to identify events subject to override.
* Edit the file ``compliance_meta_by_source.csv`` to supply appropriate fields and values.

The `csv` file provides three columns: `filter name`, `field name`, and `value`.  Filter names in the `conf` file must match one or more
corresponding `filter name` rows in the `csv` file.  The `field name` column obeys the following convention:

   * `.splunk.index` to specify an alternate `value` for index.
   * `.splunk.source` to specify an alternate `value` for source.
   * `.splunk.sourcetype` to specify an alternate `value` for sourcetype (only changing this if a downstream
    TA is present, or if a custom TA is present.)
   * `fields.fieldname` where `fieldname` will become the name of an indexed field sent to Splunk with the supplied `value`.    

This file construct is best shown by an example. Here is an example of a ``compliance_meta_by_source.conf`` file and its corresponding ``compliance_meta_by_source.csv`` file:

```
filter f_test_test {
   host("something-*" type(glob)) or
   netmask(192.168.100.1/24)
};
```


```
f_test_test,.splunk.index,"pciindex"
f_test_test,fields.compliance,"pci"
```

Ensure that the filter names in the `conf` file match
one or more rows in the `csv` file. Any incoming message with a hostname starting with `something-` or arriving from a netmask
of `192.168.100.1/24` will match the `f_test_test` filter, and the corresponding entries in the `csv` file will be checked for overrides.
The new index is `pciindex`, and an indexed field named `compliance` will be sent to Splunk with its value set to `pci`.
To add additional overrides, add another `filter foo_bar {};` stanza to the `conf` file, then add appropriate entries to the `csv` file
that match the filter names to the overrides.

Take care that your syntax is correct; for more information on proper syslog-ng syntax, see the syslog-ng
[documentation](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.24/administration-guide/57#TOPIC-1298086).
A syntax error will cause the runtime process to abort in the "preflight" phase at startup.

To update your changes, restart SC4S.

### Set source value as 'sc4s'

User can set the source field value to 'sc4s' by using the `SC4S_SET_SOURCE_AS_SC4S` variable.

**Note:** If the source field value is specified in a local parser or the splunk_metadata.csv file, it will take precedence over the `SC4S_SET_SOURCE_AS_SC4S` variable and overwrite the source field value.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_SET_SOURCE_AS_SC4S | yes or no(default) | Set the source field value to 'sc4s'. |

## Drop all data by IP or subnet (deprecated)

Using `vendor_product_by_source` to null queue is now a deprecated task. See the supported method for dropping data in [Filtering events from output](https://splunk.github.io/splunk-connect-for-syslog/main/sources/#filtering-events-from-output).

## Splunk Connect for Syslog output templates (syslog-ng templates)

Splunk Connect for Syslog uses the syslog-ng template mechanism to format the output event that will be sent to Splunk.
These templates can format the messages in a number of ways, including straight text and JSON, and can utilize the many syslog-ng
"macros" fields to specify what gets placed in the event delivered to the destination. The following table is a list of the templates
used in SC4S, which can be used for metadata override.  New templates can also be added by the
administrator in the "local" section for local destinations; pay careful attention to the syntax as the templates are "live"
syslog-ng config code.

| Template name       | Template contents                        |  Notes                                                           |
|---------------------|------------------------------------------|------------------------------------------------------------------|
| t_standard          | ${DATE} ${HOST} ${MSGHDR}${MESSAGE}      |  Standard template for most RFC3164 (standard syslog) traffic.   |
| t_msg_only          | ${MSGONLY}                               |  syslog-ng $MSG is sent, no headers (host, timestamp, etc.) .     |
| t_msg_trim          | $(strip $MSGONLY)                        |  Similar to syslog-ng $MSG with whitespace stripped.                               |
| t_everything        | ${ISODATE} ${HOST} ${MSGHDR}${MESSAGE}   |  Standard template with ISO date format.                         |
| t_hdr_msg           | ${MSGHDR}${MESSAGE}                      |  Useful for non-compliant syslog messages.                        |
| t_legacy_hdr_msg    | ${LEGACY_MSGHDR}${MESSAGE}               |  Useful for non-compliant syslog messages.                        |
| t_hdr_sdata_msg     | ${MSGHDR}${MSGID} ${SDATA} ${MESSAGE}    |  Useful for non-compliant syslog messages.                        |
| t_program_msg       | ${PROGRAM}[${PID}]: ${MESSAGE}           |  Useful for non-compliant syslog messages.                        |
| t_program_nopid_msg | ${PROGRAM}: ${MESSAGE}                   |  Useful for non-compliant syslog messages.                        |
| t_JSON_3164         | $(format-json --scope rfc3164<br>--pair PRI="<$PRI>"<br>--key LEGACY_MSGHDR<br>--exclude FACILITY<br>--exclude PRIORITY)   |  JSON output of all RFC3164-based syslog-ng macros.  Useful with the "fallback" sourcetype to aid in new filter development. |
| t_JSON_5424         | $(format-json --scope rfc5424<br>--pair PRI="<$PRI>"<br>--key ISODATE<br>--exclude DATE<br>--exclude FACILITY<br>--exclude PRIORITY)  |  JSON output of all RFC5424-based syslog-ng macros; for use with RFC5424-compliant traffic. |
| t_JSON_5424_SDATA   | $(format-json --scope rfc5424<br>--pair PRI="<$PRI>"<br>--key ISODATE<br>--exclude DATE<br>--exclude FACILITY<br>--exclude PRIORITY)<br>--exclude MESSAGE  |  JSON output of all RFC5424-based syslog-ng macros except for MESSAGE; for use with RFC5424-compliant traffic. |

# About eBPF
eBPF helps mitigate congestion of single heavy data stream by utilizing multithreading and is used with `SC4S_SOURCE_LISTEN_UDP_SOCKETS`.
To leverage this feature you need your host OS to be able to use eBPF and must run Docker or Podman in privileged mode.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_ENABLE_EBPF=yes  | yes or no(default) | Use eBPF to leverage multithreading when consuming from a single connection. |
|SC4S_EBPF_NO_SOCKETS=4 | integer | Set number of threads to use. For optimal performance this should not be less than the value set for  `SC4S_SOURCE_LISTEN_UDP_SOCKETS`. |

To run Docker or Podman in privileged mode, edit the service file `/lib/systemd/system/sc4s.service` to add the `--privileged ` flag to the Docker or Ppodman run command:
```bash
ExecStart=/usr/bin/podman run \
        -e "SC4S_CONTAINER_HOST=${SC4SHOST}" \
        -v "$SC4S_PERSIST_MOUNT" \
        -v "$SC4S_LOCAL_MOUNT" \
        -v "$SC4S_ARCHIVE_MOUNT" \
        -v "$SC4S_TLS_MOUNT" \
        --privileged \
        --env-file=/opt/sc4s/env_file \
        --health-cmd="/healthcheck.sh" \
        --health-interval=10s --health-retries=6 --health-timeout=6s \
        --network host \
        --name SC4S \
        --rm $SC4S_IMAGE
```
# Change your status port

Use `SC4S_LISTEN_STATUS_PORT` to change the "status" port used by the internal health check process. The default value is `8080`.

# Parallelize
Use the parallelize feature to manage TCP congestion when using single heavy-data streams.

This feature can be used with `SC4S_PARALLELIZE_NO_PARTITION`.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_ENABLE_PARALLELIZE=yes  | yes or no(default) | Use parallelize to leverage multithreading when consuming from a single TCP connection. |
|SC4S_PARALLELIZE_NO_PARTITION=4 | Integer | Set the number of threads to use, the default value is 4. |





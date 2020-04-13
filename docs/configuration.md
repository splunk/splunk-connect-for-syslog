# SC4S Configuration Variables

Other than device filter creation, SC4S is almost entirely controlled by environment variables.  Here are the categories
and variables needed to properly configure SC4S for your environment.

## Global Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SPLUNK_HEC_URL | url | URL(s) of the Splunk endpoint, can be a single URL space seperated list |
| SPLUNK_HEC_TOKEN | string | Splunk HTTP Event Collector Token |

* NOTE:  Do _not_ configure HEC Acknowledgement when deploying the HEC token on the Splunk side; the underlying syslog-ng http
destination does not support this feature.  Moreover, HEC Ack would significantly degrade performance for streaming data such as
syslog.


## Splunk HEC Destination Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_GLOBAL | yes | Send events to Splunk using HEC |
| SC4S_DEST_SPLUNK_HEC_CIPHER_SUITE | comma separated list | Open SSL cipher suite list |
| SC4S_DEST_SPLUNK_HEC_SSL_VERSION |  comma separated list | Open SSL version list |
| SC4S_DEST_SPLUNK_HEC_TLS_CA_FILE | path | Custom trusted cert file |
| SC4S_DEST_SPLUNK_HEC_TLS_VERIFY | yes(default) or no | verify HTTP(s) certificate |
| SC4S_DEST_SPLUNK_HEC_WORKERS | numeric | Number of destination workers (default: 10 threads).  This should rarely need to be changed; consult sc4s community for advice on appropriate setting in extreme high- or low-volume environments. |

## Alternate Destination Configuration

Alternate destinations other than HEC can be configured in SC4S. Global and/or source-specific forms of the
variables below can be used to send data to alternate destinations.

* NOTE:  The administrator is responsible for ensuring that the alternate destinations are configured in the
local mount tree, and that syslog-ng properly parses them.

* NOTE:  Do not include `d_hec` in any list of alternate destinations.  The configuration of the default HEC destination is configured
separately from that of the alternates below.


| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_GLOBAL_ALTERNATES | Comma or space-separated list of syslog-ng destinations | Send all sources to alternate destinations |
| SC4S_DEST_\<SOURCE\>_ALTERNATES | Comma or space-separated list of syslog-ng destiinations  | Send specific sources to alternate syslog-ng destinations, e.g. SC4S_DEST_CISCO_ASA_ALTERNATES |

## SC4S Disk Buffer Configuration

Disk buffers in SC4S are allocated _per destination_.  In the future as more destinations are supported, a separate list of variables
will be used for each.  This is why you see the `DEST_SPLUNK_HEC` in the variable names below.

* NOTE:  "Reliable" disk buffering offers little advantage over "normal" disk buffering, at a significant performance penalty.
For this reason, normal disk buffering is recommended.

* NOTE:  If you add destinations locally in your configuration, pay attention to the _cumulative_ buffer requirements when allocating local
disk.

* NOTE:  Disk buffer storage is configured via container volumes and is persistent between restarts of the conatiner.
Be sure to account for disk space requirements on the local sc4s host when creating the container volumes in your respective
runtime environment (outlined in the "getting started" runtime docs). These volumes can grow significantly if there is
an extended outage to the SC4S destinations (HEC endpoints). See the "SC4S Disk Buffer Configuration" section on the Configruation
page for more info.

* NOTE:  The values for the variables below represent the _total_ sizes of the buffers for the destination.  These sizes are divded by the
number of workers (threads) when setting the actual syslog-ng buffer options, because the buffer options apply to each worker rather than the
entire destination.  Pay careful attention to this when using the "BYOE" version of SC4S, where direct access to the syslog-ng config files
may hide this nuance.  Lastly, be sure to factor in the syslog-ng data structure overhead (approx. 2x raw message size) when calculating the
total buffer size needed. To determine the proper size of the disk buffer, consult the "Data Resilience" section below.

* NOTE: When changing the disk buffering directory, the new directory must exist.  If it doesn't, then syslog-ng will fail to start.

* NOTE: When changing the disk buffering directory, if buffering has previously occurd on that instance, a persist file may exist which will prevent syslog-ng from changing the directory.


| Variable | Values/Default   | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_DISKBUFF_ENABLE | yes(default) or no | Enable local disk buffering  |
| SC4S_DEST_SPLUNK_HEC_DISKBUFF_RELIABLE | yes or no(default) | Enable reliable/normal disk buffering (normal recommended) |
| SC4S_DEST_SPLUNK_HEC_DISKBUFF_MEMBUFSIZE | bytes (10241024) | Memory buffer size in bytes (used with reliable disk buffering) |
| SC4S_DEST_SPLUNK_HEC_DISKBUFF_MEMBUFLENGTH |messages (15000) | Memory buffer size in message count (used with normal disk buffering) |
| SC4S_DEST_SPLUNK_HEC_DISKBUFF_DISKBUFSIZE | bytes (53687091200) | size of local disk buffer in bytes (default 50 GB) |
| SC4S_DEST_SPLUNK_HEC_DISKBUFF_DIR | path | location to store the diskbuffering files |

## Archive File Configuration

This feature is designed to support "compliance" archival of all messages. Instructions for enabling this feature are included
in each "getting started" runtime document. The files will be stored in a folder structure using the naming pattern
``${YEAR}/${MONTH}/${DAY}/${fields.sc4s_vendor_product}_${YEAR}${MONTH}${DAY}${HOUR}${MIN}.log"``.
This pattern will create one file per minute for each "vendor_product", with records formatted using syslog-ng's EWMM template.

**WARNING POTENTIAL OUTAGE CAUSING CONSEQUENCE**

SC4S does not prune the files that are created. The administrator must provide a means of log rotation to prune files
and/or move them to an archival system to avoid exhaustion of disk space.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_ARCHIVE_GLOBAL | yes or undefined | Enable archive of all vendor_products |
| SC4S_ARCHIVE_LISTEN_<VENDOR_PRODUCT> | yes(default) or undefined | See sources section of documentation enables selective archival |


## Syslog Source Configuration

| Variable | Values/Default | Description |
|----------|----------------|-------------|
| SC4S_LISTEN_DEFAULT_TLS_PORT | undefined or 6514 | Enable a TLS listener on port 6514 |
| SC4S_SOURCE_TLS_OPTIONS | See openssl | List of SSl/TLS protocol versions to support |
| SC4S_SOURCE_TLS_CIPHER_SUITE | See openssl | List of Ciphers to support |
| SC4S_SOURCE_TCP_MAX_CONNECTIONS | 2000 | Max number of TCP Connections |
| SC4S_SOURCE_TCP_IW_SIZE | 20000000 | Initial Window size |
| SC4S_SOURCE_TCP_FETCH_LIMIT | 2000 | Number of events to fetch from server buffer at once |
| SC4S_SOURCE_UDP_SO_RCVBUFF | 1703936 | UDP server buffer size in bytes. Make sure that the host OS kernel is configured [similarly](gettingstarted/index.md#prerequisites). |
| SC4S_SOURCE_LISTEN_UDP_SOCKETS | 5 | Number of kernel sockets per active UDP port, which configures multi-threading of the UDP input buffer in the kernel to prevent packet loss.  Total UDP input buffer is the multiple of SC4S_SOURCE_LISTEN_UDP_SOCKETS * SC4S_SOURCE_UDP_SO_RCVBUFF |
| SC4S_SOURCE_STORE_RAWMSG | undefined or "no" | Store unprocessed "on the wire" raw message in the RAWMSG macro for use with the "fallback" sourcetype.  Do _not_ set this in production; substantial memory and disk overhead will result. Use for log path/filter development only. |

## Syslog Source TLS Certificate Configuration

* Create a folder ``/opt/sc4s/tls`` if not already done as part of the "getting started" process.
* Uncomment the appropriate mount line in the unit or yaml file (again, documented in the "getting started" runtime documents).
* Save the server private key in PEM format with NO PASSWORD to ``/opt/sc4s/tls/server.key``
* Save the server certificate in PEM format to ``/opt/sc4s/tls/server.pem``
* Add the following line to ``/opt/sc4s/env_file``

```dotenv
SC4S_SOURCE_TLS_ENABLE=yes
```

## SC4S metadata configuration

### Log Path overrides of index or metadata

A key aspect of SC4S is to properly set Splunk metadata prior to the data arriving in Splunk (and before any TA processing takes place).  The filters will apply the proper index, source, sourcetype, host, and timestamp metadata automatically by individual data source.  Proper values for this metadata, including a recommended index and output format (template), are included with all "out-of-the-box" log paths included with SC4S and are chosen to properly interface with the corresponding TA in Splunk.  The administrator will need to ensure all recommneded indexes be created to accept this data if the defaults are not changed.

It is understood that default values will need to be changed in many installations. To accomodate this, each filter consults a lookup file that is mounted to the container (by default `/opt/sc4s/local/context/splunk_index.csv`) and is populated with defaults on the first run of SC4S after being set up according to the "getting started" runtime documents.  This is a CSV file containing a "key" that is referenced in the log path for each data source.  These keys are documented in the individual source files in this section, and allow one to override Splunk metadata either in whole or part. The use of this file is best shown by example.  Here is the "Sourcetype and Index Configuration" table from the Juniper Netscreen source documentation page in this section:

| key                    | sourcetype          | index          | notes         |
|------------------------|---------------------|----------------|---------------|
| juniper_netscreen      | netscreen:firewall  | netfw          | none          |
| juniper_idp            | juniper:idp         | netfw          | none          |

Here is a snippet from the `splunk_indexes.csv` file:

```bash
#juniper_sslvpn,index,netfw
juniper_netscreen,index,ns_index
#juniper_nsm,index,netfw

```

The columns in this file are `key`, `metadata`, and `value`.  By default, the keys in this file are "commented out", but in reality CSV files
cannot have comments so the `#` simply causes a mismatch to the key reference, effectively "commenting" it out.  Therefore, to ensure there
is a match from the log path that references this file, be sure to remove the leading `#`.  Once this is done, the following changes can be
made by modifying and/or adding rows in the table and specifying one or more of the following `metadata`/`value` pairs for a given `key`:

   * `index` to specify an alternate `value` for index
   * `source` to specify an alternate `value` for source
   * `host` to specify an alternate `value` for host
   * `sourcetype` to specify an alternate `value` for sourcetype (be _very_ careful when changing this; only do so if an upstream
    TA is _not_ being used, or a custom TA (built by you) is being used.)
   * `sc4s_template` to specify an alternate `value` for the syslog-ng template that will be used to format the event that will be
   indexed by Splunk.  Changing this carries the same warning as the sourcetype above; this will affect the upstream TA.  The template
   choices are documented elsewhere in this "Configuration" section.

In this case, the `juniper_netscreen` key is "uncommented" (thereby enabling it), and the new index used for that data source will be
`ns_index`.

In general, for most deployments the index should be the only change needed; other default metadata should almost
never be overridden (particularly for the "Out of the Box" data sources).  Even then, care should be taken when considering any alternates,
as the defaults for SC4S were chosen with best practices in mind.

The `splunk_indexes.csv` file should also be appended to (with a "commented out" default for the index) when building custom SC4S log paths
(filters).  Care should be taken during filter design to choose appropriate index, sourctype and template defaults, so that admins are not
compelled to override them.


### Override index or metadata based on host, ip, or subnet (compliance overrides)

In other cases it is appropriate to provide the same overrides but based on PCI scope, geography, or other criterion rather than globally.
This is accomplished by the use of a file that uniquely identifies these source exceptions via syslog-ng filters,
which maps to an associated lookup of alternate indexes, sources, or other metadata.  In addition, (indexed) fields can also be
added to futher classify the data.

* The `conf` and `csv` files referenced below will be populated into the `/opt/sc4s/local/context` directory when SC4S is run for the first
time after being set up according to the "getting started" runtime documents, in a similar fashion to `splunk_indexes.csv`.  After this first-time population of the files takes place, they can be edited (and SC4S restarted) for the changes to take effect.  To get started:

* Edit the file ``compliance_meta_by_source.conf`` to supply uniquely named filters to identify events subject to override.
* Edit the file ``compliance_meta_by_source.csv`` to supply appropriate field(s) and values.

The three columns in the `csv` file are `filter name`, `field name`, and `value`.  Filter names in the `conf` file must match one or more
corresonding `filter name` rows in the `csv` file.  The `field name` column obeys the following convention:

   * `.splunk.index` to specify an alternate `value` for index
   * `.splunk.source` to specify an alternate `value` for source
   * `.splunk.sourcetype` to specify an alternate `value` for sourcetype (be _very_ careful when changing this; only do so if a downstream
    TA is _not_ being used, or a custom TA (built by you) is being used.)
   * `fields.fieldname` where `fieldname` will become the name of an indexed field sent to Splunk with the supplied `value`    

This file construct is best shown by an example.  Here is a sample ``compliance_meta_by_source.conf`` file:

```
filter f_test_test {
   host("something-*" type(glob)) or
   netmask(192.168.100.1/24)
};
```
and the corresponding ``compliance_meta_by_source.csv`` file:

```
f_test_test,.splunk.index,"pciindex"
f_test_test,fields.compliance,"pci"
```

First off, ensure that the filter name(s) in the `conf` file match
one or more rows in the `csv` file. In this case, any incoming message with a hostname starting with `something-` or arriving from a netmask
of `192.168.100.1/24` will match the `f_test_test` filter, and the corresponding entries in the `csv` file will be checked for overrides.
In this case, the new index is `pciindex`, and an indexed field named `compliance` will be sent to Splunk, with it's value set to `pci`.
To add additional overrides, simply add another `filter foo_bar {};` stanza to the `conf` file, and add appropriate entries to the `csv` file
that match the filter name(s) to the overrides you deisre.

* IMPORTANT:  The files above are actual syslog-ng config file snippets that get parsed directly by the underlying syslog-ng
process.  Take care that your syntax is correct; for more information on proper syslog-ng syntax, see the syslog-ng
[documentation](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.24/administration-guide/57#TOPIC-1298086).
A syntax error will cause the runtime process to abort in the "preflight" phase at startup.

Finally, to update your changes for the systemd-based runtimes, restart SC4S using the commands:
```
sudo systemctl daemon-reload
sudo systemctl restart sc4s
```

For the Docker Swarm runtime, redeploy the updated service using the command:
```
docker stack deploy --compose-file docker-compose.yml sc4s
```

## Dropping all data by ip or subnet

In some cases rogue or port-probing data can be sent to SC4S from misconfigured devices or vulnerability scanners. Update
the `vendor_product_by_source.conf` filter `f_null_queue` with one or more ip/subnet masks to drop events without
logging. Note that drop metrics will be recorded.


## Splunk Connect for Syslog output templates (syslog-ng templates)

Splunk Connect for Syslog utilizes the syslog-ng template mechanism to format the output payload (event) that will be sent to Splunk.  These templates can format the messages in a number of ways (straight text, JSON, etc.) as well as utilize the many syslog-ng "macros" (fields) to specify what gets placed in the payload that is delivered to the destination.  Here is a list of the templates used in SC4S, which can be used in the metadata override section immediately above.  New templates can also be added by the administrator in the "local" section for local destinations; pay careful attention to the syntax as the templates are "live" syslog-ng config code.

| Template name    | Template contents                        |  Notes                                                           |
|------------------|------------------------------------------|------------------------------------------------------------------|
| t_standard       | ${DATE} ${HOST} ${MSGHDR}${MESSAGE}      |  Standard template for most RFC3164 (standard syslog) traffic    |
| t_msg_only       | ${MSGONLY}                               |  syslog-ng $MSG is sent, no headers (host, timestamp, etc.)      |
| t_msg_trim       | $(strip $MSGONLY)                        |  As above with whitespace stripped                               |
| t_everything     | ${ISODATE} ${HOST} ${MSGHDR}${MESSAGE}   |  Standard template with ISO date format                          |
| t_hdr_msg        | ${MSGHDR}${MESSAGE}                      |  Useful for non-compliant syslog messages                        |
| t_legacy_hdr_msg | ${LEGACY_MSGHDR}${MESSAGE}               |  Useful for non-compliant syslog messages                        |
| t_hdr_sdata_msg  | ${MSGHDR}${MSGID} ${SDATA} ${MESSAGE}    |  Text-based representation of RFC5424-compliant syslog messages  |
| t_JSON_3164      | $(format-json --scope rfc3164<br>--pair PRI="<$PRI>"<br>--key LEGACY_MSGHDR<br>--exclude FACILITY<br>--exclude PRIORITY)   |  JSON output of all RFC3164-based syslog-ng macros.  Useful with the "fallback" sourcetype to aid in new filter development. |
| t_JSON_5424      | $(format-json --scope rfc5424<br>--pair PRI="<$PRI>"<br>--key ISODATE<br>--exclude DATE<br>--exclude FACILITY<br>--exclude PRIORITY)  |  JSON output of all RFC5424-based syslog-ng macros; for use with RFC5424-compliant traffic. |

## Data Resilience - Local Disk Buffer Configuration

SC4S provides capability to minimize the number of lost events if the connection to all the Splunk Indexers goes down. This capability utilizes the disk buffering feature of Syslog-ng. SC4S receives a response from the Splunk HTTP Event Collector (HEC) when a message is received successfully. If a confirmation message from the HEC endpoint is not received (or a “server busy” reply, such as a “503” is sent), the load balancer will try the next HEC endpoint in the pool.  If all pool members are exhausted (such as would occur if there were a full network outage to the HEC endpoints), events will queue to the local disk buffer on the SC4S Linux host. SC4S will continue attempting to send the failed events while it buffers all new incoming events to disk. If the disk space allocated to disk buffering fills up then SC4S will stop accepting new events and subsequent events will be lost. Once SC4S gets confirmation that events are again being received by one or more indexers, events will then stream from the buffer using FIFO queueing. The number of events in the disk buffer will reduce as long as the incoming event volume is less than the maximum SC4S (with the disk buffer in the path) can handle. When all events have been emptied from the disk buffer, SC4S will resume streaming events directly to Splunk.

For more detail on the Syslog-ng behavior the documentation can be found here: https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.22/administration-guide/55#TOPIC-1209280

SC4S has disk buffering enabled by default and it is strongly recommended that you keep it on, however this feature does have a performance cost.
Without disk buffering enabled SC4S can handle up to 345K EPS (800 bytes/event avg)
With “Normal” disk buffering enabled SC4S can handle up to 60K EPS (800 bytes/event avg) -- This is still a lot of data!

To guard against data loss it is important to configure the appropriate type and amount of storage for SC4S disk buffering. To estimate the storage allocation, follow these steps:
* Start with your estimated maximum events per second that each SC4S server will experience. Based on the maximum throughput of SC4S with disk buffering enabled, the conservative estimate for maximum events per second would be 60K (however, you should use the maximum rate in your environment for this calculation, not the max rate SC4S can handle). 
* Next is your average estimated event size based on your data sources. It is common industry practice to estimate log events as 800 bytes on average. 
* Then, factor in the maximum length of connectivity downtime you want disk buffering to be able to handle. This measure is very much dependent on your risk tolerance.
* Lastly, syslog-ng imposes significant overhead to maintain its internal data structures (primarily macros) so that the data can be properly "played back" upon network restoration.  This overhead currently runs at about 1.7x above the total storage size for the raw messages themselves, and can be higher for "fallback" data sources due to the overlap of syslog-ng macros (data fields) containing some or all of the original message.


For example, to protect against a full day of lost connectivity from SC4S to all your indexers at maximum throughput the calculation would look like the following...

60,000 EPS * 86400 seconds * 800 bytes * 1.7 = 6.4 TB of storage

To configure storage allocation for the SC4S disk buffering, do the following...
* Edit the file /opt/sc4s/default/env_file
* Add the SC4S_DEST_SPLUNK_HEC_DISKBUFF_DISKBUFSIZE variable to the file and set the value to the number of bytes based on your estimation (e.g. 7050240000000 in the example above)
* Splunk does not recommend reducing the disk allocation below 500 GB
* Restart SC4S

Given that in a connectivity outage to the Indexers events will be saved and read from disk until the buffer is emptied, it is ideal to use the fastest type of storage available. For this reason, NVMe storage is recommended for SC4S disk buffering.

It is best to design your deployment so that the disk buffer will drain after connectivity is restored to the Splunk Indexers (while incoming data continues at the same general rate).  Since "your mileage may vary" with different combinations of data load, instance type, and disk subsystem performance, it is good practice to provision a box that performs twice as well as is required for your max EPS. This headroom will allow for rapid recovery after a connectivity outage.

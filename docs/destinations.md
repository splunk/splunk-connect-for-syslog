
# Supported SC4S destinations

You can configure Splunk Connect for Syslog to use any destination available in syslog-ng OSE. Helpers manage configuration for the three most common destination needs:

* Splunk HEC, 
* RFC5424 Syslog, 
* and Legacy BSD Syslog.

**Note:** Some external SIEM systems do not correctly parse host information. Instead of extracting the host from the message, they immediately rely on the header. SC4S, as a relay, places its own IP address in the UDP or TCP header, which is the correct behavior. In this situation, the SIEM may display the SC4S IP as the source IP, but this is not a fault of SC4S.

# HEC destination

## Configuration options

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_URL | url | URL of the Splunk endpoint, this can be a single URL or a space-separated list. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_TOKEN | string | Splunk HTTP Event Collector token. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT". |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_TLS_VERIFY | yes(default) or no | Verify HTTP(s) certificates. |
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_HTTP_COMPRESSION       | yes or no(default) | Compress outgoing HTTP traffic using the gzip method. |

## HTTP Compression

HTTP traffic compression helps to reduce network bandwidth usage when sending to a HEC destination. SC4S currently supports gzip for compressing transmitted traffic.
Using the gzip compression algorithm can result in lower CPU load and increased utilization of RAM. The algorithm may also cause a decrease in performance by 6% to 7%.
Compression affects the content but does not affect the HTTP headers. Enable batch packet processing to make the solution efficient, as this allows compression of a large number of logs at once.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_&lt;ID&gt;_HTTP_COMPRESSION       | yes or no(default) | Compress outgoing HTTP traffic using the gzip method. |


# Syslog standard destination

The use of "syslog" as a network protocol has been defined in Internet Engineering Task Force standards RFC5424, RFC5425, and RFC6587.

## Configuration options

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SYSLOG_&lt;ID&gt;_HOST | fqdn or ip | The FQDN or IP of the target. |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_PORT | number | 601 is the default when framed, 514 is the default when not framed. |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_IETF | yes/no, the default value is yes. | Use IETF Standard frames. |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_TRANSPORT | tcp,udp,tls. The default value is tcp. |  |
| SC4S_DEST_SYSLOG_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT". |

### Send RFC5424 with frames

In this example, SC4S will send Cisco ASA events as RFC5424 syslog to a third party system.

The message format will be similar to:
```123 <166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID```.

The destination name is taken from the environment variable, each destination must have a unique name. This value should be short and meaningful.

```bash
#env_file
SC4S_DEST_SYSLOG_MYSYS_HOST=172.17.0.1
SC4S_DEST_SYSLOG_MYSYS_PORT=514
SC4S_DEST_SYSLOG_MYSYS_MODE=SELECT
```

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-cisco_asa_d_syslog_mysys.conf
application sc4s-lp-cisco_asa_d_syslog_mysys[sc4s-lp-dest-select-d_syslog_mysys] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}"
        and 'asa' eq "${fields.sc4s_product}"
    };    
};
```

### Send RFC5424 without frames

In this example SC4S will send Cisco ASA events to a third party system without frames. 

The message format will be similar to:
```<166>1 2022-02-02T14:59:55.000+00:00 kinetic-charlie - - - - %FTD-6-430003: DeviceUUID```.

```bash
#env_file
SC4S_DEST_SYSLOG_MYSYS_HOST=172.17.0.1
SC4S_DEST_SYSLOG_MYSYS_PORT=514
SC4S_DEST_SYSLOG_MYSYS_MODE=SELECT
# set to #yes for ietf frames
SC4S_DEST_SYSLOG_MYSYS_IETF=no 
```

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-cisco_asa_d_syslog_mysys.conf
application sc4s-lp-cisco_asa_d_syslog_mysys[sc4s-lp-dest-select-d_syslog_mysys] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}"
        and 'asa' eq "${fields.sc4s_product}"
    };    
};
```


# Legacy BSD

In many cases, the actual configuration required is Legacy BSD syslog which is not a standard and was documented in RFC3164.

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_BSD_&lt;ID&gt;_HOST | fqdn or ip | The FQDN or IP of the target. |
| SC4S_DEST_BSD_&lt;ID&gt;_PORT | number, the default is 514. |  |
| SC4S_DEST_BSD_&lt;ID&gt;_TRANSPORT | tcp,udp,tls, the default is tcp. |  |
| SC4S_DEST_BSD_&lt;ID&gt;_MODE | string | "GLOBAL" or "SELECT". |

### Send legacy BSD

The message format will be similar to:
```<134>Feb  2 13:43:05.000 horse-ammonia CheckPoint[26203]```.

```bash
#env_file
SC4S_DEST_BSD_MYSYS_HOST=172.17.0.1
SC4S_DEST_BSD_MYSYS_PORT=514
SC4S_DEST_BSD_MYSYS_MODE=SELECT
```

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-cisco_asa_d_bsd_mysys.conf
application sc4s-lp-cisco_asa_d_bsd_mysys[sc4s-lp-dest-select-d_bsd_mysys] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}"
        and 'asa' eq "${fields.sc4s_product}"
    };    
};
```

# Multiple destinations

SC4S can send data to multiple destinations. In the original setup the default destination accepts all events. This ensures that at least one destination receives the event, helping to avoid data loss due to misconfiguration. The provided examples demonstrate possible options for configuring additional HEC destinations.

## Send all events to the additional destination

After adding this example to your basic configuration SC4S will send all events both to `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_OTHER_URL`.
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=GLOBAL
```

## Send only selected events to the additional destination

After adding this example to your basic configuration SC4S will send Cisco IOS events to `SC4S_DEST_SPLUNK_HEC_OTHER_URL`.
```bash
#Note "OTHER" should be a meaningful name
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${SPLUNK_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=SELECT
```

```c
application sc4s-lp-cisco_ios_dest_fmt_other[sc4s-lp-dest-select-d_hec_fmt_other] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}"
        and 'asa' eq "${fields.sc4s_product}"
    };
};
```

## Use different index names per destination

When sending to multiple Splunk deployments, the target indexes may differ between them. You can override metadata (such as index) for a specific destination without affecting the default one.

Configure the alternate destination in SELECT mode:

```bash
#env_file
SC4S_DEST_SPLUNK_HEC_OTHER_URL=https://other-splunk:8088
SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=${OTHER_HEC_TOKEN}
SC4S_DEST_SPLUNK_HEC_OTHER_TLS_VERIFY=no
SC4S_DEST_SPLUNK_HEC_OTHER_MODE=SELECT
```

Then create a selector that both selects events for the destination and overrides the index:

```c
#filename: /opt/sc4s/local/config/app_parsers/selectors/sc4s-lp-cisco_dest_fmt_other.conf
block parser sc4s-lp-cisco_dest_other_parser() {
    channel {
        rewrite {
            r_set_splunk_dest_default(
                index('cisco_alt_index')
            );
        };
    };
};
application sc4s-lp-cisco_dest_fmt_other[sc4s-lp-dest-select-d_hec_fmt_other] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}";
    };
    parser { sc4s-lp-cisco_dest_other_parser(); };
};
```

With this configuration, Cisco events are sent to both destinations: the default HEC uses default index, while the OTHER HEC uses `cisco_alt_index`. Do mind that this index may still be overriden later (for example by metadata.csv) so it may be necessary to use a postfilter instead.

!!! note "Note" 
    Placeholder note for possible confilcts like metadata.csv!

# Send events to MDL federated indexes (Experimental)

MDL federated index destinations are named `~.federated.<name>`. SC4S does not validate index names, so it can send events to these destinations without any code changes. To do this, add a HEC destination for MDL and rewrite the index for that destination only. The default destination keeps using the standard SC4S indexes.

## Index naming

Use the SC4S index as `<name>`. For example, events that SC4S sends to `netfw` are sent to `~.federated.netfw` on the MDL destination. This keeps the index categories SC4S already uses. For the list of default indexes, see [Create indexes within Splunk](gettingstarted/getting-started-splunk-setup.md#step-1-create-indexes-within-splunk).

## Configure the MDL destination

1. Add the MDL HEC destination to your `env_file`. With `GLOBAL` mode, SC4S sends every event to both the default destination and the MDL destination.

    ```bash
    #env_file
    SC4S_DEST_SPLUNK_HEC_MDL_URL=https://mdl-hec.example.com:8088
    SC4S_DEST_SPLUNK_HEC_MDL_TOKEN=<MDL HEC token>
    SC4S_DEST_SPLUNK_HEC_MDL_TLS_VERIFY=no
    SC4S_DEST_SPLUNK_HEC_MDL_MODE=GLOBAL
    ```

    `MDL` is the destination ID. SC4S names the destination `d_hec_fmt_<id>` in lowercase, which here is `d_hec_fmt_mdl`. If you choose a different ID, change `d_hec_fmt_mdl` in the next step to match.

2. Create the following configuration file:

    ```c
    #filename: /opt/sc4s/local/config/app_parsers/app-dest-mdl_federated.conf
    block parser sc4s_dest_mdl_parser() {
        channel {
            rewrite {
                set("~.federated.${.splunk.index}", value(".splunk.index"));
            };
        };
    };

    application sc4s-lp_fmt_mdl[sc4s-lp-dest-select-d_hec_fmt_mdl] {
        filter {
            not ('splunk' eq "${fields.sc4s_vendor}" and 'sc4s' eq "${fields.sc4s_product}")
        };
        parser { sc4s_dest_mdl_parser(); };
    };
    ```

3. Restart SC4S.

SC4S now adds the `~.federated.` prefix to the index of every event it sends to the MDL destination. The filter excludes SC4S internal events, such as metrics and SC4S logs, so they keep their original indexes, for example `_metrics`. Without the filter, Splunk silently drops SC4S metrics sent to a renamed index.

## Send only selected sources to MDL

For a partial rollout, set `SC4S_DEST_SPLUNK_HEC_MDL_MODE=SELECT` and replace the filter in the `sc4s-lp_fmt_mdl` application with one that matches the sources you want to send. Only events that match the filter are sent to the MDL destination. All other events, including SC4S internal events, are sent only to the default destination.

```c
application sc4s-lp_fmt_mdl[sc4s-lp-dest-select-d_hec_fmt_mdl] {
    filter {
        'cisco' eq "${fields.sc4s_vendor}"
        and 'asa' eq "${fields.sc4s_product}"
    };
    parser { sc4s_dest_mdl_parser(); };
};
```

## Splunk requirements

* Ingest Processor can route these events with an index partition, for example `index equals "~.federated.netfw"`, or with a sourcetype partition. The index partition matches even though no index with that name exists in Splunk.
* Leave "Selected Indexes" empty on the MDL HEC token. If the token is restricted to selected indexes, HEC rejects `~.federated.*` indexes with a `400` error. SC4S does not retry events that HEC rejects with `400`, and the other events after the rejected one in the same batch are lost too.
* An index named `~.federated.<name>` cannot exist in Splunk, so events that are not routed elsewhere are stored in the `lastChanceIndex`. If no `lastChanceIndex` is configured, HEC still accepts the events, but Splunk drops them. Splunk logs a warning in `splunkd.log` only the first time this happens for each index.

# Advanced topic: Configure filtered alternate destinations 

You may require more granularity for a specific data source. For example, you may want to send all Cisco ASA debug traffic to Cisco Prime for analysis. To accommodate this, filtered alternate destinations let you supply a filter to redirect a portion of a source's traffic to a list of alternate destinations and, optionally, prevent matching events from being sent to Splunk. You configure this using environment variables:

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_ALT_FILTER | syslog-ng filter | Filter to determine which events are sent to alternate destinations. |
| SC4S_DEST_&lt;VENDOR_PRODUCT&gt;_FILTERED_ALTERNATES | Comma or space-separated list of syslog-ng destinations.  | Send filtered events to alternate syslog-ng destinations using the VENDOR_PRODUCT syntax, for example, `SC4S_DEST_CISCO_ASA_FILTERED_ALTERNATES`.  |

This is an advanced capability, and filters and destinations using proper syslog-ng syntax must be constructed before using this functionality.

The regular destinations, including the primary HEC destination or configured archive destination, for example `d_hec` or `d_archive`, are not included for events matching the configured alternate
destination filter. If an event matches the filter, the list of filtered alternate destinations completely replaces any mainline destinations, including defaults and global or source-based standard alternate destinations. Include them in the filtered destination list if desired.

Since the filtered alternate destinations completely replace the mainline destinations, including HEC to Splunk, a filter that matches all traffic can be used with a destination list that does not include the standard HEC destination to effectively turn off HEC for a given data source.

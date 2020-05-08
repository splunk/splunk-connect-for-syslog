# Introduction
When using Splunk Connect for Syslog to onboard a data source, the SC4S filter (or "log path") performs the operations that are traditionally performed at index-time by the corresponding Technical Add-on installed there. These index-time operations include linebreaking, sourcetype setting and timestamping. For this reason, if a data source is exclusively onboarded using SC4S then you will not need to install its corresponding Add-On on the indexers. You must, however, install the Add-on on the search head(s) for the user communities interested in this data source. 

SC4S "unique" filters are based either on the port upon which events arrive or the hostname/CIDR block from which they are sent. The "soup" filters run for events that arrive on port 514 (default for syslog), and contain regex and other syslog-specific parsers to identify events from a specific source, apply the correct sourcetype, and set other metadata. Data sources which generate events that are not unique enough to accurately identify with soup filters _must_ employ the "unique" filters (port/hostname/CIDR block) instead -- the soup filters are unavailable for these sources. 

## The SC4S "fallback" sourcetype

If SC4S receives an event on port 514 which has no soup filter, that event will be given a "fallback" sourcetype. If you see events in Splunk with the fallback sourcetype, then you should figure out what source the events are from and determine why these events are not being sourcetyped correctly. The most common reason for events categorized as "fallback" is the lack of a SC4S filter for that source, and in some cases a misconfigured relay which alters the integrity of the message format. In most cases this means a new SC4S filter must be developed. In this situation you can either build a filter or file an issue with the community to request help. 

The "fallback" sourcetype is formatted in JSON to allow the administrator to see the constituent syslog-ng "macros" (fields) that have been autmaticially parsed by the syslog-ng server An RFC3164 (legacy BSD syslog) "on the wire" raw message is usually (but unfortunately not always) comprised of the following syslog-ng macros, in this order and spacing:
```
<$PRI> $HOST $LEGACY_MSGHDR$MESSAGE
```
These fields can be very useful in building a new filter for that sourcetype.  In addition, the indexed field `sc4s_syslog_format` is helpful in determining if the incoming message is standard RFC3164. A value of anything other than `rfc3164` or `rfc5424_strict` indicates a vendor purturbation of standard syslog, which will warrant more careful examination when building a filter.

## Splunk Connect for Syslog and Splunk metadata

A key aspect of SC4S is to properly set Splunk metadata prior to the data arriving in Splunk (and before any TA processing takes place.  The filters will apply the proper index, source, sourcetype, host, and timestamp metadata automatically by individual data source.  Proper values for this metadata (including a recommended index) are included with all "out-of-the-box" log paths included with SC4S and are chosen to properly interface with the corresponding TA in Splunk.  The administrator will need to ensure all recommneded indexes be created to accept this data if the defaults are not changed.

It is understood that default values will need to be changed in many installations.  Each source documented in this section has a table entitled "Sourcetype and Index Configuration", which highlights the default index and sourcetype for each source.  See the section "SC4S metadata configuration" in the "Configuration" page for more information on how to override the default values in this table.

## Unique listening ports

SC4S supports unique listening ports for each source technology/log path (e.g. Cisco ASA), which is useful when the device is
sending data on a port different from the typical default syslog port (UDP port 514).  In some cases, when the source device emits data that
is not able to be distinguished from other device types, a unique port is sometimes required.  The specific environment variables used for
setting "unique ports" are outlined in each source document in this section.

In most cases only one "unique port" is needed for each source.  However, SC4S also supports multiple network listening ports per source,
which can be useful for a narrow set of compliance use cases. When configuring a source port variable to enable multiple ports, use a
comma-separated list with no spaces (e.g. `SC4S_LISTEN_CISCO_ASA_UDP_PORT=5005,6005`).

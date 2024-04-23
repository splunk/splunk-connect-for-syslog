# Splunk setup
To ensure proper syslog processing with SC4S, it is necessary to do additional set up in the Splunk instance:
1. create the appropriate indexes within Splunk
2. configure the HTTP Event Collector accordingly.


## Create Indexes

SC4S maps each sourcetype to the following indexes by default.

* `email`
* `epav`
* `epintel`
* `infraops`
* `netauth`
* `netdlp`
* `netdns`
* `netfw`
* `netids`
* `netlb`
* `netops`
* `netwaf`
* `netproxy`
* `netipam`
* `oswin`
* `oswinsec`
* `osnix`
* `print`
* `_metrics` (Optional opt-in for SC4S operational metrics; ensure this is created as a metrics index)

SC4S can also be customized to use different indexes, which also have to be created in Splunk.

## Configure the Splunk HTTP Event Collector
See [Splunk documentation](https://docs.splunk.com/Documentation/Splunk/9.2.1/Data/UsetheHTTPEventCollector) for specific HEC configuration instructions based on your
Splunk type.

Mind the following practices specific to HEC for SC4S:
1. Make sure that the HEC token created for SC4S has permissions to add events to 'main', '_metrics', and all event destinations indexes.
2. You can leave "Selected Indexes" blank on the token configuration page so that the token has access to
all indexes, including the `lastChanceIndex`.  If this list is populated, extreme care must be taken to keep it up to date, as an attempt to
send data to an index that is not in this list results in a `400` error from the HEC endpoint and the `lastChanceIndex` will not be
consulted if the index specified in the event is not configured on Splunk.  Note that one bad message can prevent and entire batch from being sent to Splunk.
3. If you are not using TLS on SC4S, turn off SSL on global settings for HEC in Splunk.
4. SC4S traffic must be sent to HEC endpoints configured directly on the indexers rather than an intermediate tier of heavy forwarders.  

### Load balancing
You need a load balancing mechanism between SC4S and Splunk indexers. Note that this should not to be confused with load balancing between [sources and SC4S](../lb.md).

- Splunk Cloud provides an internal ELB on TCP 443.

- For Splunk Enterprise set up your Splunk HTTP Event Collector with the HEC endpoints behind a load balancer. 
  - An external load balancer simplifies long-term maintenance by eliminating the need to manually keep the list of HEC URLs specified in sc4s current. Set up a load balancer using virtual IP and configured for https round robin without sticky session. 
  - If a load balancer is not available, you can configure a list of HEC endpoint URLs with native syslog-ng load balancing. For internal load balancing of syslog-ng it is recommended that:
    - you balance to ten or fewer indexers
    - HEC is used exclusively for syslog
    - SC4S extracts timestamps from messages (default behavior) rather than using the time of receiving the message.

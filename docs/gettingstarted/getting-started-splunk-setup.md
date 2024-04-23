# Splunk setup
## Create Indexes

SC4S maps each sourcetype to the following indexes by default. SC4S can also be customized to use different indexes that you can create in Splunk. 

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

## Configure the Splunk HTTP Event Collector

1. Set up your Splunk HTTP Event Collector with the HEC endpoints behind a load balancer round-robin configuration. If you do not have a load balancer in your configuration, you can configure a list of HEC endpoint URLs with native syslog-ng load balancing.

  Note that an external load balancer simplifies long-term
maintenance, but if a load balancer is not
available, native load balancing can be used with ten or fewer indexers where HEC is used exclusively for syslog.

  SC4S traffic must be sent to HEC endpoints configured directly on the indexers rather than
an intermediate tier of heavy forwarders.  

2. Create a HEC token to be used by SC4S. Make sure the token has permissions to add events to 'main', '_metrics', and all
event destinations indexes.

3. You can leave "Selected Indexes" blank on the token configuration page so that the token has access to
all indexes, including the `lastChanceIndex`.  If this list is populated, extreme care must be taken to keep it up to date, as an attempt to
send data to an index that is not in this list results in a `400` error from the HEC endpoint and the `lastChanceIndex` will not be
consulted if the index specified in the event is not configured on Splunk.  Note that one bad message can prevent and entire batch from being sent to Splunk.

4. If you are not using TLS on SC4S, turn off SSL on global settings for HEC in Splunk. See [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)
or [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q) for specific HEC configuration instructions based on your
Splunk type.


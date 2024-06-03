# Splunk setup
To ensure proper integration for SC4S and Splunk, perform the following tasks in your Splunk instance:

1. Create your SC4S indexes in Splunk.
2. Configure your HTTP event collector.


## Step 1: Create indexes within Splunk

SC4S maps each sourcetype to the following indexes by default. You will also need to create these indexes in Splunk:

* `email`
* `epav`
* `epintel`
* `fireeye`
* `gitops`
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

If you use custom indexes in SC4S you must also create them in Splunk. See [Create custom indexes]( https://docs.splunk.com/Documentation/Splunk/9.2.1/Indexer/Setupmultipleindexes) for more information.

## Step 2: Configure your HTTP event collector

See [Use the HTTP event collector](https://docs.splunk.com/Documentation/Splunk/9.2.1/Data/UsetheHTTPEventCollector) for HEC configuration instructions based on your
Splunk type.

Keep in mind the following best practices specific to HEC for SC4S:
* Make sure that the HEC token created for SC4S has permissions to write to `_metrics` and all event destination indexes.
* You can leave "Selected Indexes" blank on the token configuration page so that the token has access to
all indexes, including the `lastChanceIndex`.  If you do populate this field, take extreme care to keep it up to date; an attempt to
send data to an index that is not in this list results in a `400` error from the HEC endpoint. The `lastChanceIndex` will not be
consulted if the index specified in the event is not configured on Splunk and the entire batch is then not sent to Splunk.
* SC4S traffic should be sent to HEC endpoints configured directly on the indexers rather than an intermediate tier of heavy forwarders.
* SC4S traffic must be sent to HEC endpoints that are configured directly on the indexers.  

### Create a load balancing mechanism
In some configurations, you should ensure output balancing from SC4S to Splunk indexers. To do this, you create a load balancing mechanism between SC4S and Splunk indexers. Note that this should not be confused with load balancing between [sources and SC4S](../lb.md). 

When configuring your load balancing mechanism, Keep in mind the following:

* Splunk Cloud provides an internal ELB on TCP 443.
* For Splunk Enterprise set up your Splunk HTTP Event Collector with the HEC endpoints behind a load balancer. 
* An external load balancer simplifies long-term maintenance by eliminating the need to manually keep the list of HEC URLs specified in SC4S current. Set up a load balancer using virtual IP and configured for https round-robin without sticky session. 
* If a load balancer is not available, you can configure a list of HEC endpoint URLs with native syslog-ng load balancing. For internal load balancing of syslog-ng you should:
    * Load balance ten or fewer indexers.
    * Use HEC exclusively for syslog.
    * Have SC4S extract timestamps from messages (default behavior) rather than use the time of receipt for the message.

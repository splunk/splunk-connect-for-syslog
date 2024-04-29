# Splunk setup
## Create Indexes

SC4S is pre-configured to map each sourcetype to a typical index. For new installations, it is best practice to create them in Splunk when
using the SC4S defaults. SC4S can be easily customized to use different indexes if desired.

* email
* epav
* epintel
* infraops
* netauth
* netdlp
* netdns
* netfw
* netids
* netlb
* netops
* netwaf
* netproxy
* netipam
* oswin
* oswinsec
* osnix
* print
* _metrics (Optional opt-in for SC4S operational metrics; ensure this is created as a metrics index)

## Configure the Splunk HTTP Event Collector

- Set up the Splunk HTTP Event Collector with the HEC endpoints behind a load balancer (VIP) configured for https round robin *WITHOUT* sticky
session.  Alternatively, a list of HEC endpoint URLs can be configured in SC4S (native syslog-ng load balancing) if no load balancer is in
place.  In most scenarios the recommendation is to use an external load balancer, as that makes longer term
maintenance simpler by eliminating the need to manually keep the list of HEC URLs specified in sc4s current. However, if a LB is not
available, native load balancing can be used with 10 or fewer Indexers where HEC is used exclusively for syslog.

  In either case, it is _strongly_ recommended that SC4S traffic be sent to HEC endpoints configured directly on the indexers rather than
an intermediate tier of HWFs.  
- Create a HEC token that will be used by SC4S and ensure the token has access to place events in main, _metrics, and all indexes used as
event destinations.

* NOTE: It is recommended that the "Selected Indexes" on the token configuration page be left blank so that the token has access to
_all_ indexes, including the `lastChanceIndex`.  If this list is populated, extreme care must be taken to keep it up to date, as an attempt to
send data to an index not in this list will result in a `400` error from the HEC endpoint. Furthermore, the `lastChanceIndex` will _not_ be
consulted in the event the index specified in the event is not configured on Splunk.  Keep in mind just _one_ bad message will "taint" the
whole batch (by default 1000 events) and prevent the entire batch from being sent to Splunk.
* In case you are not using TLS on SC4S- turn off SSL on global settings for HEC in Splunk.
- Refer to [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)
or [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q) for specific HEC configuration instructions based on your
Splunk type.


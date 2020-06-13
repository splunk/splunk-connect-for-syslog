# Vendor - Splunk


## Product - Splunk Connect for Syslog (SC4S)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4740/                                                                 |
| Product Manual | https://splunk-connect-for-syslog.readthedocs.io/en/master/  |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| sc4s:events    | Internal events from the SC4S container and underlying syslog-ng process                                |
| sc4s:metrics   | syslog-ng operational metrics that will be delivered directly to a metrics index in Splunk              |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| sc4s_events    | all            | main           | none           |
| sc4s_metrics   | all            | em_metrics     | none           |

### Filter type

SC4S events and metrics are generated automatically and no specific ports or filters need to be configured for the collection of this data.

### Setup and Configuration

* No specific requirements are required for the collection of sc4s internal events.
* Metrics data is _not_ collected by default; it is an opt-in set by the variable `SC4S_DEST_SC4S_METRICS_HEC`. See the "Options"
section below for details.

### Options

| Variable                          | default   | description    |
|-----------------------------------|-----------|----------------|
| SC4S_DEST_SPLUNK_SC4S_EVENTS_HEC  | no        | When Splunk HEC is disabled globally set to "yes" to enable this specific source |
| SC4S_DEST_SPLUNK_SC4S_METRICS_HEC | no        | Set to "yes" to send metrics via HEC to Splunk (opt-in).  Metrics are _not_ enabled by default when HEC is enabled globally. |

### Verification

SC4S will generate versioning events at startup. These startup events can be used to validate HEC is set up properly on the Splunk side.

```
index=<asconfigured> sourcetype=sc4s:events | stats count by host
```
Metrics can be observed via the "Analytics-->Metrics" navigation in the Search and Reporting app in Splunk.
* NOTE:  The presentation of metrics is undergoing active development; the delivery of metrics is currently considered an experimental feature.

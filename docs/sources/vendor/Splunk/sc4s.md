# Splunk Connect for Syslog (SC4S)

## Key facts

* Internal events

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4740/>                                                                 |
| Product Manual | <https://splunk-connect-for-syslog.readthedocs.io/en/latest/>  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| sc4s:events    | Internal events from the SC4S container and underlying syslog-ng process                                |
| sc4s:metrics   | syslog-ng operational metrics that will be delivered directly to a metrics index in Splunk              |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| splunk_sc4s_events    | all            | main           | none           |
| splunk_sc4s_metrics   | all            | _metrics     | none           |
| splunk_sc4s_fallback   | all            | main     | none           |

### Filter type

SC4S events and metrics are generated automatically and no specific ports or filters need to be configured for the collection of this data.

## Setup and Configuration

* The default index used for sc4s metrics will be "_metrics"
* Metrics data is collected by default as traditional events; use of Splunk Metrics is enabled by an opt-in set by the variable `SC4S_DEST_SPLUNK_SC4S_METRICS_HEC`. See the "Options"
section below for details.

## Options

| Variable                          | default   | description    |
|-----------------------------------|-----------|----------------|
| SC4S_DEST_SPLUNK_SC4S_METRICS_HEC | multi2        | `event` produce metrics as plain text events; `single` produce metrics using Splunk Enterprise 7.3 single metrics format; `multi` produce metrics using Splunk Enterprise >8.1 multi metric format  `multi2` produces improved (reduced resource consumption) multi metric format |
| SC4S_SOURCE_MARK_MESSAGE_NULLQUEUE | yes | (yes|no) null_queue messages with the body of -- MARK -- |

### Verification

SC4S will generate versioning events at startup. These startup events can be used to validate HEC is set up properly on the Splunk side.

```
index=<asconfigured> sourcetype=sc4s:events | stats count by host
```

Metrics can be observed via the "Analytics-->Metrics" navigation in the Search and Reporting app in Splunk.

* NOTE:  The presentation of metrics is undergoing active development; the delivery of metrics is currently considered an experimental feature.

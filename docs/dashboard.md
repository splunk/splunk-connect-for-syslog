# SC4S Metrics and Events Dashboard
The SC4S Metrics and Events Dashboard lets you monitor crucial metrics and event flows for all the SC4S instances sending data to a chosen Splunk platform.


## Functionalities

### Overview metrics
The dashboard displays the cumulative sum of received and dropped messages for all SC4S instances in a chosen interval and for the specified time range. By default the interval is set to 30 seconds and the time range is 15 minutes.

The Received Messages panel can be used as a heartbeat metric. A healthy SC4S instance should send at least one message per 30 seconds. This metrics message is included in the count.

The Dropped Messages panel should remain at a constant level of 0. If SC4S drops messages due to filters, slow performance, or for any other reason, the number of dropped messages will persist until the instance restarts. This panel does not include potential UDP messages dropped from the port buffer, which SC4S is not able to track.

### Single instance metrics
You can display the instance name and SC4S version for a chosen SC4S instance.
SC4S is available in versions greater than or equal to 3.16.0.

The dashboard also displays a timechart of deltas for received, queued, and dropped messages for a chosen SC4S instance.

### Single instance events
The dashboard helps to analyze traffic processed by an SC4S instance by visualizing the following events data:

- total number of events
- distributions of events by index
- trends of events by index
- data parsers in use
- applied tags

## Installation
1. In Splunk platform open `Search` -> `Dashboards`.  
2. Click on `Create New Dashboard` and make an empty dashboard. Be sure to choose `Classic Dashboards`.
3. In the `Edit Dashboard` view go to `Source` and replace the initial xml with the contents of [dashboard/dashboard.xml](https://github.com/splunk/splunk-connect-for-syslog/blob/main/dashboard/dashboard.xml) published in the SC4S repository.
4. After saving the changes your dashboard will be ready to use.
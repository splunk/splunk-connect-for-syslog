# SC4S Metrics and Events Dashboard
SC4S Metrics and Events Dashboard enables monitoring crucial metrics and events flow of all the SC4S instances sending data to a chosen Splunk platform.


## Functionalities

### Overview metrics
The dashboard displays the cumulative sum of received and dropped messages of all SC4S instances in chosen interval and for the specified time range. It is 30 seconds span in a 15 minutes window by default.

Received messages panel can be used as a heart beat metric, since a healthy SC4S instance should send at least one message per 30 seconds. This is a metrics message and it's included in the count.

Dropped messages panel should remain at a constant level of 0. If SC4S drops messages due to filters, slow performance or other reasons, the number of dropped messages will be there until the instance restart. This does not include potential UDP messages dropped from the port buffer, which SC4S is completely unaware of.

### Single instance metrics
The user can display instance name and SC4S version for a chosen SC4S instance.
SC4S version is available in versions >=3.15.0.

The dashboard also displays a timechart of deltas of received, queued and dropped messages for a chosen SC4S instance.

### Single instance events
The dashboard helps to analyze traffic processed by an SC4S instance by visualizing the following events data:

- total number of events
- distributions of events by index
- trends of events by index
- data parsers in use
- applied tags

## Installation
1. In Splunk platform open `Search` -> `Dashboards`.  
2. Click on `Create New Dashboard` and make an empty dashboard. Be sure to choose `Classic Dashboards`. Other configuration options are not relevant.  
3. In the `Edit Dashboard` view go to `Source` and replace the initial xml with the contents of [dashboard/dashboard.xml](https://github.com/splunk/splunk-connect-for-syslog/blob/sc4s_dashboard_110/dashboard/dashboard.xml) published in the SC4S repository.
4. After saving the changes your dashboard will be ready to use.
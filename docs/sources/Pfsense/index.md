# Vendor - pfSense

All pfSense based firewalls


## Product


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/1527/                                                                 |
| Product Manual | https://docs.netgate.com/pfsense/en/latest/monitoring/copying-logs-to-a-remote-host-with-syslog.html?highlight=syslog |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| pfsense:filterlog  | None |
| pfsense:* | All programs other than filterlog |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| pfsense      | pfsense     | netops          | none          |
| pfsense_filterlog      | pfsense:filterlog      | netfw          | none          |

### Filter type

Source does not provide a hostname, port or IP based filter is required

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Configure a dedicated SC4S port OR configure IP filter 
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_PFSENSE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_PFSENSE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_PFSENSE | no | Enable archive to disk for this specific source |
| SC4S_DEST_PFSENSE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=pfsense:filterlog | stats count by host
```

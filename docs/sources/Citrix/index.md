# Vendor - Citrix

## Product - Netscaler ADC/SDX

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2770/                                                                 |
| Product Manual | https://docs.citrix.com/en-us/citrix-adc/12-1/system/audit-logging/configuring-audit-logging.html |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| citrix:netscaler:syslog         | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| citrix_netscaler         | citrix:netscaler:syslog         | netfw          | none           |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Follow vendor configuration steps per Product Manual above. Ensure the data format selected is "DDMMYYYY" 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CITRIX_NETSCALER_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the port number defined |
| SC4S_LISTEN_CITRIX_NETSCALER_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the port number defined |
| SC4S_DEST_CITRIX_NETSCALER_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cp_log
```

Verify timestamp, and host values match as expected   

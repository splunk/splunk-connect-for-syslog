# Vendor - Dell EMC 


## Product - Powerswitch N Series

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Product Manual | unknown  |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:emc:powerswitch:n        | None                                                                                               |
| nix:syslog     | Non conforming messages                                                                                          |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dellemc_powerswitch_n      | all       | netops          | none          |

### Filter type

Message Format

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_DELLEMC_POWERSWITCH_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_DELLEMC_POWERSWITCH_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_DELLEMC_POWERSWITCH | no | Enable archive to disk for this specific source |
| SC4S_DEST_DELLEMC_POWERSWITCH_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=dell:emc:powerswitch:n | stats count by host
```

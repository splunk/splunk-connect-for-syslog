# Vendor - F5


## Product - BigIP

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2680/                                                                 |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| f5:bigip:syslog        | None                                                                                                    |
| f5:bigip:irule    | None                                                                                         |
| nix:syslog     | None                                                                                          |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| f5_bigip      | f5:bigip:syslog       | netops          | none          |
| f5_bigip_irule    | f5:bigip:syslog      | netops          | none          |
| f5_bigip_nix    | nix:syslog      | netops          | if `f_f5_bigip` is not set the index osnix will be used          |

### Filter type

Must be identified by host or ip assignment. Update the filter `f_f5_bigip` or configure a dedicated port as required

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_F5_BIGIP_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_F5_BIGIP_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_F5_BIGIP | no | Enable archive to disk for this specific source |
| SC4S_DEST_F5_BIGIP_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=f5:bigip:*| stats count by host
```

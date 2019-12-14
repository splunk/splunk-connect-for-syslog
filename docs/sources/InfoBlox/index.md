# Vendor - Infoblox

## Product - NIOS

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2934/                                                                 |
| Product Manual | http://dloads.infoblox.com/direct/appliance//NIOS/NIOS_AdminGuide_6.10.pdf    |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| infoblox:dns        | None                                                                                                    |
| infoblox:dhcp    | None                                                                                         |
| infoblox:threat     | None                                                                                          |
| nix:syslog     | None                                                                                          |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| infoblox_dns      | infoblox:dns       | netdns          | none          |
| infoblox_dhcp    | infoblox:dhcp      | netipam          | none          |
| infoblox_threat    | infoblox:threat      | netids          | none          |
| nix_syslog    | nix:syslog      | osnix          | none          |

### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_INFOBLOX_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_INFOBLOX_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_INFOBLOX | no | Enable archive to disk for this specific source |
| SC4S_DEST_INFOBLOX_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=infoblox:*| stats count by host
```

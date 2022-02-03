# Vendor - Infoblox

Warning: Despite the TA indication this data source is CIM compliant the all versions of NIOS including the most recent available as of 2019-12-17 do not support the DNS data model correctly. For DNS security use cases use Splunk Stream instead.

## Product - NIOS

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2934/                                                                 |
| Product Manual | https://docs.infoblox.com/display/ILP/NIOS?preview=/8945695/43728387/NIOS_8.4_Admin_Guide.pdf   |


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
| infoblox_nios_dns      | infoblox:dns       | netdns          | none          |
| infoblox_nios_dhcp    | infoblox:dhcp      | netipam          | none          |
| infoblox_nios_threat    | infoblox:threatprotect      | netids          | none          |
| infoblox_nios_audit    | infoblox:audit      | netops          | none          |
| infoblox_nios_fallback    | infoblox:port      | netops          | none          |

### Filter type

Must be identified by host or ip assignment. Update the filter `f_infoblox` or configure a dedicated port as required

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_INFOBLOX_NIOS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_INFOBLOX_NIOS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_INFOBLOX_NIOS | no | Enable archive to disk for this specific source |
| SC4S_DEST_INFOBLOX_NIOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=infoblox:*| stats count by host
```

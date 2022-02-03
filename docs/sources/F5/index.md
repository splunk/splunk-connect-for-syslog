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
| f5:bigip:ltm:http:irule | None |
| f5:bigip:gtm:dns:request:irule | None |
| f5:bigip:gtm:dns:response:irule | None |
| f5:bigip:ltm:failed:irule | None |
| f5:bigip:asm:syslog | None |
| f5:bigip:apm:syslog | None |
| nix:syslog     | None                                                                                          |
| f5:bigip:ltm:access_json | User defined configuration via irule producing a RFC5424 syslog event with json content within the message field `<111>1 2020-05-28T22:48:15Z foo.example.com F5 - access_json - {"event_type":"HTTP_REQUEST", "src_ip":"10.66.98.41"}` This source type requires a customer specific Splunk Add-on for utility value |


### Index Configuration

| key            | index          | notes          |
|----------------|----------------|----------------|
| f5_bigip       | netops          | none          |
| f5_bigip_irule | netops          | none          |
| f5_bigip_asm   | netwaf          | none          |
| f5_bigip_apm   | netops          | none          |
| f5_bigip_nix   | netops          | if `f_f5_bigip` is not set the index osnix will be used          |
| f5_bigip_access_json | netops | none |

### Filter type

* MSGPARSE: sourcetypes with the exception of f5:bigip:syslog
* `f5:bigip:syslog` Must be identified by host or ip assignment. Update the `vendor_product_by_source.conf` filter `f_f5_bigip` or configure a dedicated port as required

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used,
* the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration.

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_F5_BIGIP_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_F5_BIGIP_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_F5_BIGIP | no | Enable archive to disk for this specific source |
| SC4S_DEST_F5_BIGIP_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=f5:bigip:*| stats count by host
```

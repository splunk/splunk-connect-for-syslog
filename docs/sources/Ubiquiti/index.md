# Vendor - Ubiquiti - Unifi

All Ubiquity Unfi firewalls, switches, and access points share a common syslog configuration via the NMS.


* Login to NMS
* Navigate to settings
* Navigate to Site 
* Enable Remote syslog server
* Enter hostname and port
* Update ``vi /opt/sc4s/local/context/vendor_product_by_source.conf `` update the host or ip mask for ``f_ubiquiti_unifi_fw`` to identify USG firewalls

## Product - Unifi Switch and Access Points 

Unifi devices are managed using the Network Management Controller


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4107/                                                                 |
| Product Manual | https://https://help.ubnt.com/    |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ubnt  | Used when no sub source type is required by add on |
| ubnt:fw  | USG events |
| ubnt:threat | USG IDS events    |
| ubnt:switch  | Unifi Switches |
| ubnt:wireless  | Access Point logs |


### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ubiquiti_unifi      | ubnt     | netops          | none          |
| ubiquiti_unifi_fw      | ubnt:fw       | netfw          | none          |

### Filter type

MSG Parse: This filter parses message content. Some unifi devices do not have the ability to send host name in the syslog message.
When host name is provided if the hostname begins with an upper case U it will be discarded as a "model" number when configuring device names in the 
NMS use valid RFC dns names (lower case a-z numbers 0-9 and dash).

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_UBIQUITI_UNIFI_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_UBIQUITI_UNIFI_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_UBIQUITI_UNIFI | no | Enable archive to disk for this specific source |
| SC4S_DEST_UBIQUITI_UNIFI_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=zscalernss-* | stats count by host
```

# Vendor - Proofpoint

## Product - Proofpoint Protection Server

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3080/                                                                 |
| Product Manual | https://proofpointcommunities.force.com/community/s/article/Remote-Syslog-Forwarding                    |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| pps_filter_log |                                                                               |
|  pps_mail_log  | This sourcetype will conflict with sendmail itself, so will require that the PPS send syslog on a dedicated port or be uniquely identifiable with a hostname glob or CIDR block if this sourcetype is desired for PPS.   |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| proofpoint_pps_filter        | pps_filter_log       | email          | none          |
| proofpoint_pps_sendmail      | pps_mail_log       | email          | none          |


### Filter type

MSG Parse: This filter parses message content
* NOTE:  This filter will simply parse the syslog message itself, and will _not_ perform the (required) re-assembly of related
messages to create meaningful final output.  This will require follow-on processing in Splunk.

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Follow vendor configuration steps per referenced Product Manual

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_PROOFPOINT_PPS_TCP_PORT    | empty string     | Enable a TCP port for this specific vendor product using the number defined.  |
| SC4S_PROOFPOINT_PPS_UDP_PORT    | empty string     | Enable a UDP port for this specific vendor product using the number defined.  |
| SC4S_ARCHIVE_PROOFPOINT_PPS | no | Enable archive to disk for this specific source |
| SC4S_DEST_PROOFPOINT_PPS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

One or two sourcetypes are included in Proofpoint PPS logs.  The search below will surface both of them:

```
index=<asconfigured> sourcetype=pps_*_log | stats count by host
```
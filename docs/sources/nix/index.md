# Vendor - Nix Generic

## Product - All Products

Many appliance vendor utilize Linux and BSD distributions as the foundation of the solution when configured to provide
syslog output these devices can be monitored using the common Splunk Nix TA.

Note: This is not a replacement or alternative for use of the Splunk Universal forwarder on Linux and Unix. For server applications
the syslog only prevents full collection of events and metrics appropriate for security and operations use cases.



| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/833/                                                                 |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| nix:syslog  | None |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| nix_syslog      | nix:syslog       | osnix          | none          |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.


### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_ARCHIVE_NIX_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_NIX_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=osnix sourcetype=nix:syslog | stats count by host
```

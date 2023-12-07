# Generic *NIX

Many appliance vendor utilize Linux and BSD distributions as the foundation of the solution. When configured to log via
syslog, these devices' OS logs (from a security perspective) can be monitored using the common Splunk Nix TA.

Note: This is NOT a replacement for or alternative to the Splunk Universal forwarder on Linux and Unix. For general-purpose
server applications, the Universal Forwarder offers more comprehensive collection of events and metrics appropriate for both
security and operations use cases.

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/833/>                                                                 |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| nix:syslog  | None |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| nix_syslog      | nix:syslog       | osnix          | none          |

### Filter type

MSG Parse: This filter parses message content

## Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_DEST_NIX_SYSLOG_ARCHIVE | no | Enable archive to disk for this specific source |
| SC4S_DEST_NIX_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |


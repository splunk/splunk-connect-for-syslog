# Vendor - Dell RSA


## Product - SecureID

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2958/                                                                 |
| Product Manual | http://docs.splunk.com/Documentation/AddOns/latest/RSASecurID/About  |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| rsa:securid:syslog        | Catchall; used if a more specific source type can not be identified                                                                                                 |
| rsa:securid:admin:syslog    | None                                                                                         |
| rsa:securid:runtime:syslog     | None                                                               | rsa:securid:system:syslog     | None                                                                                          |
| nix:syslog     | None                                                                                          |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_rsa_secureid      | all       | netauth          | none          |
| dell_rsa_secureid    | nix:syslog      | osnix          | uses os_nix key of not configured bye host/ip/port          |

### Filter type

Must be identified by host or ip assignment. Update the filter `f_dell_rsa_secureid` or configure a dedicated port as required

NOTE: Java trace and exception will default to sc4s:fallback if the host/ip filter or port is not configured

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_DELL_RSA_SECUREID_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_DELL_RSA_SECUREID_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_DELL_RSA_SECUREID | no | Enable archive to disk for this specific source |
| SC4S_DEST_DELL_RSA_SECUREID_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=DELL_RSA_SECUREID:*| stats count by host
```

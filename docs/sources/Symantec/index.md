# Vendor - Symantec

## Product - Symantec Endpoint Protection

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | No Public add-on                                                               |
| Product Manual | https://support.symantec.com/us/en/article.tech242216.html                                                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| symantec:ep:syslog        | Warning the syslog method of accepting EP logs has been reported to show high data loss and is not Supported by Splunk  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| symantec_ep      | symantec:ep:syslog       | epav          | none          |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SYMANTEC_EP_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_SYMANTEC_EP_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_SYMANTEC_EP | no | Enable archive to disk for this specific source |
| SC4S_DEST_SYMANTEC_EP_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active server will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=symantec:ep:syslog | stats count by host
``

## Product - ProxySG/ASG (Bluecoat)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2758/                                                                 |
| Product Manual | https://support.symantec.com/us/en/article.tech242216.html                                                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| bluecoat:proxysg:access:kv        | Requires version TA 3.6                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| bluecoat_proxy      | bluecoat:proxysg:access:kv       | netops          | none          |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SYMANTEC_PROXY_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_SYMANTEC_PROXY_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_SYMANTEC_PROXY | no | Enable archive to disk for this specific source |
| SC4S_DEST_SYMANTEC_PROXY_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=bluecoat:proxysg:access:kv | stats count by host
```

## Product - Mail Gateway (Brightmail)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | TBD                                                            |
| Product Manual | https://support.symantec.com/us/en/article.howto38250.html                                                       |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| symantec:smg        | Requires version TA 3.6                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| symantec_brightmail      | symantec:smg     | email          | none          |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* No TA available
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SYMANTEC_BRIGHTMAIL_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_SYMANTEC_BRIGHTMAIL_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_SYMANTEC_BRIGHTMAIL | no | Enable archive to disk for this specific source |
| SC4S_DEST_SYMANTEC_BRIGHTMAIL_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_SOURCE_FF_SYMANTEC_BRIGHTMAIL_GROUPMSG | yes | Email processing events generated by the bmserver process will be grouped by host+program+pid+msg ID into a single event |
### Verification

An active mail server will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=symantec:smg | stats count by host
```

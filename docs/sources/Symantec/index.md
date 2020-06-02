# Vendor - Symantec

## Product - Symantec Endpoint Protection

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2772/                                                               |
| Product Manual | https://techdocs.broadcom.com/content/broadcom/techdocs/us/en/symantec-security-software/endpoint-security-and-management/endpoint-protection/all/Monitoring-Reporting-and-Enforcing-Compliance/viewing-logs-v7522439-d37e464/exporting-data-to-a-syslog-server-v8442743-d15e1107.html |


### Sourcetypes

| sourcetype                     | notes                                                                                                   |
|--------------------------------|---------------------------------------------------------------------------------------------------------|
| symantec:ep:syslog             | Warning the syslog method of accepting EP logs has been reported to show high data loss and is not Supported by Splunk  |
| symantec:ep:admin:syslog       | none |
| symantec:ep:agent:syslog       | none |
| symantec:ep:agt:system:syslog  | none |
| symantec:ep:behavior:syslog    | none |
| symantec:ep:packet:syslog      | none |
| symantec:ep:policy:syslog      | none |
| symantec:ep:proactive:syslog   | none |
| symantec:ep:risk:syslog        | none |
| symantec:ep:scan:syslog        | none |
| symantec:ep:scm:system:syslog  | none |
| symantec:ep:security:syslog    | none |
| symantec:ep:traffic:syslog     | none |

### Index Configuration

| key            | index          | notes          |
|----------------|----------------|----------------|
| symantec_ep    | epav           | none           |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized as follows

```
<111>1 $(date)T$(x-bluecoat-hour-utc):$(x-bluecoat-minute-utc):$(x-bluecoat-second-utc).000z $(x-bluecoat-appliance-name) bluecoat - splunk_format - c-ip=$(c-ip) Content-Type=$(quot)$(rs(Content-Type))$(quot) cs-auth-group=$(cs-auth-group) cs-bytes=$(cs-bytes) cs-categories=$(quot)$(cs-categories)$(quot) cs-host=$(cs-host) cs-ip=$(cs-ip) cs-method=$(cs-method) cs-uri-extension=$(cs-uri-extension) cs-uri-path=$(cs-uri-path) cs-uri-port=$(cs-uri-port) cs-uri-query=$(quot)$(cs-uri-query)$(quot) cs-uri-scheme=$(cs-uri-scheme) cs-User-Agent=$(quot)$(cs(User-Agent))$(quot) cs-username=$(cs-username) dnslookup-time=$(dnslookup-time) duration=$(duration) rs-status=$(rs-status) rs-version=$(rs-version) rs_Content_Type=$(rs-Content-Type) s-action=$(s-action) s-ip=$(s-ip) service.name=$(service.name) service.group=$(service.group) s-supplier-ip=$(s-supplier-ip) s-supplier-name=$(s-supplier-name) sc-bytes=$(sc-bytes) sc-filter-result=$(sc-filter-result) sc-filter-result=$(sc-filter-result) sc-status=$(sc-status) time-taken=$(time-taken) x-bluecoat-appliance-name=$(x-bluecoat-appliance-name) x-bluecoat-appliance-primary-address=$(x-bluecoat-appliance-primary-address) x-bluecoat-application-name=$(x-bluecoat-application-name) x-bluecoat-application-operation=$(x-bluecoat-application-operation) x-bluecoat-proxy-primary-address=$(x-bluecoat-proxy-primary-address) x-bluecoat-transaction-uuid=$(x-bluecoat-transaction-uuid) x-exception-id=$(x-exception-id) x-virus-id=$(x-virus-id) c-url=$(quot)$(url)$(quot) cs-Referer=$(quot)$(cs(Referer))$(quot) c-cpu=$(c-cpu) c-uri-pathquery=$(c-uri-pathquery) connect-time=$(connect-time) cs-auth-groups=$(cs-auth-groups) cs-headerlength=$(cs-headerlength) cs-threat-risk=$(cs-threat-risk) r-ip=$(r-ip) r-supplier-ip=$(r-supplier-ip) rs-time-taken=$(rs-time-taken) rs-server=$(rs(server)) s-connect-type=$(s-connect-type) s-icap-status=$(s-icap-status) s-sitename=$(s-sitename) s-source-port=$(s-source-port) s-supplier-country=$(s-supplier-country) sc-Content-Encoding=$(sc(Content-Encoding)) sr-Accept-Encoding=$(sr(Accept-Encoding)) x-auth-credential-type=$(x-auth-credential-type) x-cookie-date=$(x-cookie-date) x-cs-certificate-subject=$(x-cs-certificate-subject) x-cs-connection-negotiated-cipher=$(x-cs-connection-negotiated-cipher) x-cs-connection-negotiated-cipher-size=$(x-cs-connection-negotiated-cipher-size) x-cs-connection-negotiated-ssl-version=$(x-cs-connection-negotiated-ssl-version) x-cs-ocsp-error=$(x-cs-ocsp-error) x-cs-Referer-uri=$(x-cs(Referer)-uri) x-cs-Referer-uri-address=$(x-cs(Referer)-uri-address) x-cs-Referer-uri-extension=$(x-cs(Referer)-uri-extension) x-cs-Referer-uri-host=$(x-cs(Referer)-uri-host) x-cs-Referer-uri-hostname=$(x-cs(Referer)-uri-hostname) x-cs-Referer-uri-path=$(x-cs(Referer)-uri-path) x-cs-Referer-uri-pathquery=$(x-cs(Referer)-uri-pathquery) x-cs-Referer-uri-port=$(x-cs(Referer)-uri-port) x-cs-Referer-uri-query=$(x-cs(Referer)-uri-query) x-cs-Referer-uri-scheme=$(x-cs(Referer)-uri-scheme) x-cs-Referer-uri-stem=$(x-cs(Referer)-uri-stem) x-exception-category=$(x-exception-category) x-exception-category-review-message=$(x-exception-category-review-message) x-exception-company-name=$(x-exception-company-name) x-exception-contact=$(x-exception-contact) x-exception-details=$(x-exception-details) x-exception-header=$(x-exception-header) x-exception-help=$(x-exception-help) x-exception-last-error=$(x-exception-last-error) x-exception-reason=$(x-exception-reason) x-exception-sourcefile=$(x-exception-sourcefile) x-exception-sourceline=$(x-exception-sourceline) x-exception-summary=$(x-exception-summary) x-icap-error-code=$(x-icap-error-code) x-rs-certificate-hostname=$(x-rs-certificate-hostname) x-rs-certificate-hostname-category=$(x-rs-certificate-hostname-category) x-rs-certificate-observed-errors=$(x-rs-certificate-observed-errors) x-rs-certificate-subject=$(x-rs-certificate-subject) x-rs-certificate-validate-status=$(x-rs-certificate-validate-status) x-rs-connection-negotiated-cipher=$(x-rs-connection-negotiated-cipher) x-rs-connection-negotiated-cipher-size=$(x-rs-connection-negotiated-cipher-size) x-rs-connection-negotiated-ssl-version=$(x-rs-connection-negotiated-ssl-version) x-rs-ocsp-error=$(x-rs-ocsp-error)

```    

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

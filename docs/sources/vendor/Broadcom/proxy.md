
# ProxySG/ASG

Symantec now Broadcom ProxySG/ASG is formerly known as the "Bluecoat" proxy

Broadcom products are inclusive of products formerly marketed under Symantec and Bluecoat brands.

## Key facts

* MSG Format based filter
* The standard/default bluecoat syslog configurations are NOT supported a SC4S specific configuration is provided below
* RFC5424 without IETF Frame must use 514/TCP or 6514/TLS


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2758/                                                                 |
| Product Manual | https://support.symantec.com/us/en/article.tech242216.html                                                        |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| bluecoat:proxysg:access:kv        | Requires version TA 3.8.1                                                                                                    |
| bluecoat:proxysg:access:syslog           | Requires version TA 3.8.1                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| bluecoat_proxy      | bluecoat:proxysg:access:syslog       | netops          | none          |
| bluecoat_proxy_splunkkv      | bluecoat:proxysg:access:kv       | netproxy          | none          |


## Setup and Configuration

* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized as follows

```
<111>1 $(date)T$(x-bluecoat-hour-utc):$(x-bluecoat-minute-utc):$(x-bluecoat-second-utc)Z $(s-computername) ProxySG - splunk_format - c-ip=$(c-ip) rs-Content-Type=$(quot)$(rs(Content-Type))$(quot)  cs-auth-groups=$(cs-auth-groups) cs-bytes=$(cs-bytes) cs-categories=$(cs-categories) cs-host=$(cs-host) cs-ip=$(cs-ip) cs-method=$(cs-method) cs-uri-port=$(cs-uri-port) cs-uri-scheme=$(cs-uri-scheme) cs-User-Agent=$(quot)$(cs(User-Agent))$(quot) cs-username=$(cs-username) dnslookup-time=$(dnslookup-time) duration=$(duration) rs-status=$(rs-status) rs-version=$(rs-version) s-action=$(s-action) s-ip=$(s-ip) service.name=$(service.name) service.group=$(service.group) s-supplier-ip=$(s-supplier-ip) s-supplier-name=$(s-supplier-name) sc-bytes=$(sc-bytes) sc-filter-result=$(sc-filter-result) sc-status=$(sc-status) time-taken=$(time-taken) x-exception-id=$(x-exception-id) x-virus-id=$(x-virus-id) c-url=$(quot)$(url)$(quot) cs-Referer=$(quot)$(cs(Referer))$(quot) c-cpu=$(c-cpu) connect-time=$(connect-time) cs-auth-groups=$(cs-auth-groups) cs-headerlength=$(cs-headerlength) cs-threat-risk=$(cs-threat-risk) r-ip=$(r-ip) r-supplier-ip=$(r-supplier-ip) rs-time-taken=$(rs-time-taken) rs-server=$(rs(server)) s-connect-type=$(s-connect-type) s-icap-status=$(s-icap-status) s-sitename=$(s-sitename) s-source-port=$(s-source-port) s-supplier-country=$(s-supplier-country) sc-Content-Encoding=$(sc(Content-Encoding)) sr-Accept-Encoding=$(sr(Accept-Encoding)) x-auth-credential-type=$(x-auth-credential-type) x-cookie-date=$(x-cookie-date) x-cs-certificate-subject=$(x-cs-certificate-subject) x-cs-connection-negotiated-cipher=$(x-cs-connection-negotiated-cipher) x-cs-connection-negotiated-cipher-size=$(x-cs-connection-negotiated-cipher-size) x-cs-connection-negotiated-ssl-version=$(x-cs-connection-negotiated-ssl-version) x-cs-ocsp-error=$(x-cs-ocsp-error) x-cs-Referer-uri=$(x-cs(Referer)-uri) x-cs-Referer-uri-address=$(x-cs(Referer)-uri-address) x-cs-Referer-uri-extension=$(x-cs(Referer)-uri-extension) x-cs-Referer-uri-host=$(x-cs(Referer)-uri-host) x-cs-Referer-uri-hostname=$(x-cs(Referer)-uri-hostname) x-cs-Referer-uri-path=$(x-cs(Referer)-uri-path) x-cs-Referer-uri-pathquery=$(x-cs(Referer)-uri-pathquery) x-cs-Referer-uri-port=$(x-cs(Referer)-uri-port) x-cs-Referer-uri-query=$(x-cs(Referer)-uri-query) x-cs-Referer-uri-scheme=$(x-cs(Referer)-uri-scheme) x-cs-Referer-uri-stem=$(x-cs(Referer)-uri-stem) x-exception-category=$(x-exception-category) x-exception-category-review-message=$(x-exception-category-review-message) x-exception-company-name=$(x-exception-company-name) x-exception-contact=$(x-exception-contact) x-exception-details=$(x-exception-details) x-exception-header=$(x-exception-header) x-exception-help=$(x-exception-help) x-exception-last-error=$(x-exception-last-error) x-exception-reason=$(x-exception-reason) x-exception-sourcefile=$(x-exception-sourcefile) x-exception-sourceline=$(x-exception-sourceline) x-exception-summary=$(x-exception-summary) x-icap-error-code=$(x-icap-error-code) x-rs-certificate-hostname=$(x-rs-certificate-hostname) x-rs-certificate-hostname-category=$(x-rs-certificate-hostname-category) x-rs-certificate-observed-errors=$(x-rs-certificate-observed-errors) x-rs-certificate-subject=$(x-rs-certificate-subject) x-rs-certificate-validate-status=$(x-rs-certificate-validate-status) x-rs-connection-negotiated-cipher=$(x-rs-connection-negotiated-cipher) x-rs-connection-negotiated-cipher-size=$(x-rs-connection-negotiated-cipher-size) x-rs-connection-negotiated-ssl-version=$(x-rs-connection-negotiated-ssl-version) x-rs-ocsp-error=$(x-rs-ocsp-error) cs-uri-extension=$(cs-uri-extension) cs-uri-path=$(cs-uri-path) cs-uri-query=$(quot)$(cs-uri-query)$(quot) c-uri-pathquery=$(c-uri-pathquery)
```



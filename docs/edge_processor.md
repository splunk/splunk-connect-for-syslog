# SC4S + EP guide (Experimental)

## Basic Setup:

* Use IP of EP instance as HEC URL: `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=http://x.x.x.x:8088`
* Use token from EP Global Settings: `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=secret`
* Use EP API format: `SC4S_HEC_TEMPLATE=t_edge_hec`

## TLS:

* Switch to HTTPS at HEC: `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://x.x.x.x:8088`
* [Generate certificates](https://docs.splunk.com/Documentation/SplunkCloud/9.1.2308/EdgeProcessor/SecureForwarders)
* Upload certs at Edge Processor TLS settings
* Rename `Client cert` to `cert.pem`
* Rename `Client key` to `key.pem`
* Rename `CA Cert` to `ca_cert.pem`
* Mount dir with certs to `/etc/syslog-ng/tls/hec`
* Set path for TLS dir: `SC4S_DEST_TLS_MOUNT=/etc/syslog-ng/tls/hec`

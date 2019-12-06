# Vendor - Zscaler

## Product - All Products

The ZScaler product manual includes and extensive section of configuration for multiple Splunk TCP input ports around page
26. When using SC4S these ports are not required and should not be used. Simply configure all outputs from the NSS to utilize
the IP or host name of the SC4S instance and port 514


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3865/                                                                 |
| Product Manual | https://community.zscaler.com/t/zscaler-splunk-app-design-and-installation-documentation/4728                                                      |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| zscalernss-alerts  | Requires format customization add ``\tvendor=Zscaler\tproduct=alerts`` immediately prior to the ``\n`` in the NSS Alert Web format. See Zscaler manual for more info. |
| zscalernss-dns  | Requires format customization  add ``\tvendor=Zscaler\tproduct=dns`` immediately prior to the ``\n`` in the NSS DNS format. See Zscaler manual for more info. |
| zscalernss-web  | None    |
| zscalernss-zpa-app  | Requires format customization  add ``\tvendor=Zscaler\tproduct=zpa`` immediately prior to the ``\n`` in the Firewall format. See Zscaler manual for more info. |
| zscalernss-zpa-auth  | Requires format customization add ``\tvendor=Zscaler\tproduct=zpa_auth`` immediately prior to the ``\n`` in the Firewall format. See Zscaler manual for more info. |
| zscalernss-zpa-connector  | Requires format customization  add ``\tvendor=Zscaler\tproduct=zpa_auth_connector`` immediately prior to the ``\n`` in the LSS Connector format. See Zscaler manual for more info. |
| zscalernss-fw  | Requires format customization add ``\tvendor=Zscaler\tproduct=fw`` immediately prior to the ``\n`` in the Firewall format. See Zscaler manual for more info. |


### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| zscalernss_alerts      | zscalernss-alerts       | main          | none          |
| zscalernss_dns      | zscalernss-dns     | netdns          | none          |
| zscalernss_fw      | zscalernss-fw       | netfw          | none          |
| zscalernss_web      | zscalernss-web       | netproxy          | none          |
| zscalernss-zpa-app      | zscalernss_zpa-app       | netids          | none          |
| zscalernss-zpa-auth      | zscalernss_zpa_auth       | netauth          | none          |
| zscalernss-zpa-connector    | zscalernss_zpa_connector       | netops          | none          |


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
| SC4S_LISTEN_ZSCALER_NSS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_ZSCALER_NSS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_ZSCALER_NSS | no | Enable archive to text for this specific source |
| SC4S_DEST_ZSCALER_NSS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=zscalernss-* | stats count by host
```

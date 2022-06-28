# NSS

The ZScaler product manual includes and extensive section of configuration for multiple Splunk TCP input ports around page
26. When using SC4S these ports are not required and should not be used. Simply configure all outputs from the NSS to utilize
the IP or host name of the SC4S instance and port 514

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3865/>                                                                 |
| Product Manual | <https://community.zscaler.com/t/zscaler-splunk-app-design-and-installation-documentation/4728>                                                      |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| zscaler_nss_alerts  | Requires format customization add ``\tvendor=Zscaler\tproduct=alerts`` immediately prior to the ``\n`` in the NSS Alert Web format. See Zscaler manual for more info. |
| zscaler_nss_dns  | Requires format customization  add ``\tvendor=Zscaler\tproduct=dns`` immediately prior to the ``\n`` in the NSS DNS format. See Zscaler manual for more info. |
| zscaler_nss_web  | None    |
| zscaler_nss_fw  | Requires format customization add ``\tvendor=Zscaler\tproduct=fw`` immediately prior to the ``\n`` in the Firewall format. See Zscaler manual for more info. |

## Sourcetype and Index Configuration

| key                 | sourcetype             | index    | notes   |
|---------------------|------------------------|----------|---------|
| zscaler_nss_alerts  | zscalernss-alerts      | main     | none    |
| zscaler_nss_dns     | zscalernss-dns         | netdns   | none    |
| zscaler_nss_fw      | zscalernss-fw          | netfw    | none    |
| zscaler_nss_web     | zscalernss-web         | netproxy | none    |
| zscaler_nss_tunnel  | zscalernss-tunnel      | netops   | none    |
| zscaler_zia_audit   | zscalernss-zia-audit   | netops   | none    |
| zscaler_zia_sandbox | zscalernss-zia-sandbox | main     | none    |

### Filter type

MSG Parse: This filter parses message content

## Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
  * Select TCP or SSL transport option
  * Ensure the format of the event is customized per Splunk documentation

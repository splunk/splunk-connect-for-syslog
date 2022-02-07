# LSS

The ZScaler product manual includes and extensive section of configuration for multiple Splunk TCP input ports around page
26. When using SC4S these ports are not required and should not be used. Simply configure all outputs from the LSS to utilize
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
| zscaler_lss-app  | None |
| zscaler_lss-auth  | None |
| zscaler_lss-bba  | None |
| zscaler_lss-connector  | None |

## Sourcetype and Index Configuration

| key            | sourcetype               | index      | notes   |
|----------------|--------------------------|------------|---------|
| zscaler_lss    | zscalerlss_zpa-app       | netproxy   | none    |
| zscaler_lss    | zscalerlss_zpa_auth      | netproxy   | none    |
| zscaler_lss    | zscalerlss_zpa_auth      | netproxy   | none    |
| zscaler_lss    | zscalerlss_zpa_connector | netproxy   | none    |


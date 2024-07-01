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
| zscalerlss-zpa-app  | None |
| zscalerlss-zpa-bba  | None |
| zscalerlss-zpa-connector  | None |
| zscalerlss-zpa-auth  | None |
| zscalerlss-zpa-audit  | None |

## Sourcetype and Index Configuration

| key            | sourcetype               | index      | notes   |
|----------------|--------------------------|------------|---------|
| zscaler_lss    |zscalerlss-zpa-app, zscalerlss-zpa-bba, zscalerlss-zpa-connector, zscalerlss-zpa-auth, zscalerlss-zpa-audit | netproxy   | none    |


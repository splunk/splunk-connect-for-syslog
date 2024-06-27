## Upgrade SC4S

1. For the latest version, use the `latest` tag for the SC4S image in the sc4s.service unit file. You can also set a specific version in the unit file if desired.

```
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container3:latest"
```

2. Restart the service.
```sudo systemctl restart sc4s```

See the [release notes](https://github.com/splunk/splunk-connect-for-syslog/releases) for more information.

## Upgrade Notes
Version 3 does not introduce any breaking changes. To upgrade to version 3, review the service file and change the container reference from `container2` to `container3`.
For a step by step guide [see here](./v3_upgrade.md).

You may need to migrate legacy log paths or version 1 app-parsers for version 2. To do this, open an issue and attach the original configuration and a compressed pcap of sample data for testing. We will evaluate whether to include the source in an upcoming release.

### Upgrade from <2.23.0

* In VMware vSphere, update the ESX and vCenter sourcetype for add-on compatibility.

### Upgrade from <2

* Before upgrading to 2.x, review `sc4s.service` and manually update the differences as compared to the current version `sc4s.service`.
* The SNMP Trap feature has been removed, migrate to [Splunk Connect for SNMP](https://splunk.github.io/splunk-connect-for-snmp)
* Legacy gomplate log path template support was deprecated in 1.x and has been removed in 2.x log paths. SC4S must be migrated to an app-parser style configuration prior to upgrade.
* Check `env_file` for "MICROFOCUS_ARCSIGHT" variables and replace with CEF variables. 
* Remove "CISCO_*_LEGACY" from `env_file` and replace per the current version of `sc4s.service`. 
* New images will no longer be published to Docker. Review the current Getting Started docs and update the `sc4s.service` file accordingly.
* Internal metrics will now use the multi format by default. If your system uses unsupported versions of Splunk 8.1 or earlier, see the Configuration Documentation for information on how to revert to event or single format.
* Internal metrics will now use the `_metrics` index by default. Update `vendor_product` key 'sc4s_metrics' to change the index.
* `vendor_product_by_source` is deprecated. For null queue or dropping events, see [Filtering events from output](https://splunk.github.io/splunk-connect-for-syslog/main/sources/). This use will be removed in version 3.
* `vendor_product_by_source` is deprecated. For identification of source by host/ip see the new app-parser syntax for your applicable product.
* `SPLUNK_HEC_ALT_DESTS` is deprecated and will be ignored.
* `SC4S_DEST_GLOBAL_ALTERNATES` is deprecated and will be removed in future major versions. 
* Corrected Vendor/Product keys. See the following source documentation pages and revised configuration as part of your upgrade:
  * Zscaler (multiple changes)
  * dell_emc_powerswitch_n
  * F5_BIGIP
  * INFOBLOX
  * Dell RSA SecureID
  * ubiquiti
  * SC4S will now use "splunk" as the vendor value and "sc4s" as the product.
  * Fireye HX
  * Juniper
  * ossec
  * Palo Alto Networks
  * Pulse Connect
  * ricoh
  * tanium
  * tintri
  * Vmware esx,vcenter,nsx,horizon
  * Wallix Bastion
* Internal Changes
  * `.dest_key` field is no longer used.
  * `sc4s_vendor_product` is read only and will be removed.
  * `sc4s_vendor` now contains vendor portion of `vendor_product`.
  * `sc4s_vendor_product` now contains product portion of 'vendor_product'.
  * `sc4s_class` now contains additional data previously concatenated to `vendor_product`
  * removed `meta_key`.
* Custom "app-parsers" critical change:

```c
#Current app parsers contain one or more lines
vendor_product('value_here')
#This must change to failure to make this change will prevent sc4s from starting
vendor('value')
product('here')
```

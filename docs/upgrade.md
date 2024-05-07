# Upgrading Splunk Connect for Syslog

Splunk Connect for Syslog is updated regularly using a CI/CD development process.  The notes below outline significant changes that
must be taken into account prior and after an upgrade.  Ensure to follow specific instructions below to ensure a smooth
transition to a new version of SC4S in production.

## Upgrade process

Check the current version of SC4S by running ```sudo <docker or podman> logs SC4S```. For the latest version, use the
`latest` tag for the SC4S image in the sc4s.service unit file:

```
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container4:latest"
```

Restart the service
```sudo systemctl restart sc4s```

Using the "4" version is recommended, but a specific version can be set in the unit file if desired:

```
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container4:latest"
```

See the [release information](https://github.com/splunk/splunk-connect-for-syslog/releases) for more detail.

### Upgrade from 3.0 to 4.0

* Deprecated old OS with exceeded EOL like CentOS 7
* Deprecated BYOE

### Upgrade from 2.0 to 3.0
Version 3 does not introduce any breaking change. To upgrade to version 3 review service file and change container reference from `container2` to `container3`.
For a step by step guide [see here](./v3_upgrade.md).
Need up migrating legacy "log paths" or v1 app-parsers for v2. Open an issue with the original config attached and a compressed pcap of sample data for testing and we will evaluate inclusion of the source in an upcoming release.

### Upgrade from <2.23.0

* Vmware vsphere fix esx and vcenter sourcetype for TA compatibility

### Upgrade from <2

* Before upgrading to 2.x review sc4s.service and manually update differences compared to current doc
* EXPERIMENTAL SNMP Trap feature has been removed migrate to [Splunk Connect for SNMP](https://splunk.github.io/splunk-connect-for-snmp)
* Legacy "gomplate" log path template support was deprecated in 1.x and has been removed in 2.x log paths must be migrated to app-parser style config prior to upgrade
* Check env_file for "MICROFOCUS_ARCSIGHT" variables and replace with CEF variables see source doc
* Remove old style "CISCO_*_LEGACY" from env_file and replace per docs
* New images will no longer be published to docker.io please review current getting started docs and update the sc4s.service file accordingly
* Internal metrics will now use "multi" format by default if using unsupported versions of Splunk <8.1 see configuration doc to revert to "event" or "single" format.
* Internal metrics will now use the _metrics index by default update vendor_product key 'sc4s_metrics' to change the index
* Deprecated use of vendor_product_by_source for null queue or dropping events see See [Filtering events from output](https://splunk.github.io/splunk-connect-for-syslog/main/sources/) this use will be removed in v3
* Deprecated use of vendor_product_by_source for identification of source by host/ip see new app-parser syntax documented per applicable product
* Deprecated use of `SPLUNK_HEC_ALT_DESTS` this variable is no longer used and will be ignored
* Deprecated use of `SC4S_DEST_GLOBAL_ALTERNATES` this variable will be removed in future major versions see Destinations section in configuration
* Corrected Vendor/Product keys *BREAKING* Please see source doc pages and revise configuration as part of upgrade
  * Zscaler (multiple changes)
  * dell_emc_powerswitch_n
  * F5_BIGIP
  * INFOBLOX
  * Dell RSA SecureID
  * ubiquiti
  * SC4S will now use "splunk as the vendor value, "sc4s" as the product
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
  * `.dest_key` field is no longer used
  * `sc4s_vendor_product` is read only and will be removed
  * `sc4s_vendor` new contains "vendor" portion of vendor_product
  * `sc4s_vendor_product` new contains "product" portion of vendor product
  * `sc4s_class` new contains additional data previously concatenated to vendor_product
  * removed `meta_key`
* Custom "app-parsers" Critical Change

```c
#Current app parsers contain one or more lines
vendor_product('value_here')
#This must change to failure to make this change will prevent sc4s from starting
vendor('value')
product('here')
```

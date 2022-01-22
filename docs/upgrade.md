# Upgrading Splunk Connect for Syslog

Splunk Connect for Syslog is updated regularly using a CI/CD development process.  The notes below outline significant changes that
must be taken into account prior and after an upgrade.  Ensure to follow specific instructions below to ensure a smooth
transition to a new version of SC4S in production.

## Upgrade process
Check the current version of SC4S by running ```sudo <docker or podman> logs SC4S```. For the latest version, use the
`latest` tag for the SC4S image in the sc4s.service unit file:
```
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container:1"
```
Restart the service
```sudo systemctl restart sc4s```

Using the "1" version is recommended, but a specific version can be specified in the unit file if desired:
```
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container:1.91.0"
```
See the [release information](https://github.com/splunk/splunk-connect-for-syslog/releases) for more detail.

## Upgrade Nodes


### Upgrade from <2

* EXPERIMENTAL SNMP Trap feature has been removed migrate to [Splunk Connect for SNMP](https://splunk.github.io/splunk-connect-for-snmp)
* Legacy "gomplate" log path template support was deprecated in 1.x and has been removed in 2.x log paths must be migrated to app-parser style config prior to upgrade
* Remove old style "CISCO_*_LEGACY" from env_file and replace per docs

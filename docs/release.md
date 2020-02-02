# Release Notes

Splunk Connect for Syslog is updated regularly using a CI/CD development process.  Check back often for the latest on each release
here.  Changes that will affect current installations, as well as new and deprecated features, will be outlined below.

## Version 1.9.0

* Version string added
* Example context files added to local mount.  These example files will be updated at each release to add support for new data sources,
and the new content can be added to existing context files (without the `.example` extension).  Existing context files will _not_ be
overwritten on subsequent SC4S starts/upgrades, so ensure that content for new data sources is incorporated in existing context files.
* Support for Cisco devices sending events with no hostname has been added.

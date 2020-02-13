# Upgrading Splunk Connect for Syslog

Splunk Connect for Syslog is updated regularly using a CI/CD development process.  The notes below outline significant changes that
must be taken into account prior and after an upgrade.  Ensure to follow specific instructions below to ensure a smooth transition to
a new version of SC4S in production.

## Version 1.9.0

* Example context files have been added to the local mount `context` directory.  These example files will be updated at each release
to outline support for new data sources, which can be added to existing context files (those without the `.example` extension).
Existing context files will _not_ be overwritten on subsequent SC4S starts/upgrades, so ensure that any new content from these example
files is incorporated into existing context files.

* UNIT FILE CHANGES:  Make sure to update the unit file used to start the sc4s service with the changes included in this release. It
includes updates for proper operation with RHEL 8, and is backward-compatible with RHEL 7.7.

## Version 1.10.0

* The "Development" section outlines new instructions for operation with the vscode IDE.
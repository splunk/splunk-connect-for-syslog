# Upgrading Splunk Connect for Syslog

Splunk Connect for Syslog is updated regularly using a CI/CD development process.  The notes below outline significant changes that
must be taken into account prior and after an upgrade.  Ensure to follow specific instructions below to ensure a smooth
transition to a new version of SC4S in production.

###Upgrade process
Check the current version of SC4S by running ```sudo <docker or podman> logs SC4S```. For the latest version, use the
`latest` tag for the SC4S image in the sc4s.service unit file:
```
[Service]
Environment="SC4S_IMAGE=splunk/scs:latest"
```
Restart the service
```sudo systemctl restart sc4s```

Having latest is recommended but if some other version is required specify in the service file. For eg:
```
[Service]
Environment="SC4S_IMAGE=splunk/scs:v1.20.0"
```
Follow the link for release information  https://github.com/splunk/splunk-connect-for-syslog/releases

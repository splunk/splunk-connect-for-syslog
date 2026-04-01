# Upgrading Splunk Connect for Syslog v2 -> v3
## Upgrade process (for version newer than 2.3.0)
In general the upgrade process consists of three steps:
- change of container version
- restart of service
- validation
NOTE: Version 3 of SC4S is using alpine linux distribution as base image in opposition to previous versions which used UBI (Red Hat) image.
### Docker/Podman
#### Update container image version

In the service file: `/lib/systemd/system/sc4s.service ` container image reference should be updated to version 3 with `latest` tag:
```
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container3:latest"
```
#### Restart sc4s service

Restart the service:
```sudo systemctl restart sc4s```

#### Validate
After the above command is executed successfully, the following information with the version becomes visible in the container logs:
`sudo podman logs SC4S` for podman or `sudo docker logs SC4S` for docker.
Expected output:
```bash
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=3.0.0
starting syslog-ng 
```

If you are upgrading from version lower than 2.3.0 please refer to [this guide](./upgrade.md#upgrade-from-2230).
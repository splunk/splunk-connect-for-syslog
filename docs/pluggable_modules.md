# Pluggable modules guide:

Splunk Lite pluggable modules are predefined modules that you can enable or disable by modifying the config.yaml file. This yaml file contains a list of add-ons. See the ([config.yaml reference file](https://github.com/splunk/splunk-connect-for-syslog/blob/main/package/lite/etc/config.yaml)) for more information about this file. Once you update config.yaml you save it to /etc/syslog-ng/config.yaml.


## Install SC4S Lite using docker-compose:

The installation process is identical to the installation process for[ docker-compose for SC4S](./gettingstarted/docker-compose.md) with the following modifications.

* Use the SC4S Lite image instead of the SC4S image:
```
image: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

* Mount your config.yaml file with your add-ons to /etc/syslog-ng/config.yaml:

```
volumes:
    - /path/to/your/config.yaml:/etc/syslog-ng/config.yaml
```

## Kubernetes:

The installation process is identical to the installation process for [Kubernetes for SC4S]((./gettingstarted/k8s-microk8s.md)) with the following modifications:

* Use the SC4S Lite image instead of SC4S in values.yaml:
```
image:
  repository: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

* Mount config file to values.yaml:

```
sc4s:
    addons:
        config.yaml: |-
            ---
            addons:
                - cisco
                - paloalto
                - dell
```

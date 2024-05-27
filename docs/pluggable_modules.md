# Working with pluggable modules 

SC4S Lite pluggable modules are predefined modules that you can enable or disable by modifying your `config.yaml` file. This file contains a list of add-ons. See the example and list of available pluggable modules in ([config.yaml reference file](https://github.com/splunk/splunk-connect-for-syslog/blob/main/package/lite/etc/config.yaml)) for more information. Once you update  `config.yaml`, you mount it to the Docker container and override `/etc/syslog-ng/config.yaml`.


## Install SC4S Lite using Docker Compose

The installation process is identical to the installation process for[ Docker Compose for SC4S](./gettingstarted/docker-compose.md) with the following modifications.

* Use the SC4S Lite image instead of the SC4S image:
```
image: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

* Mount your `config.yaml` file with your add-ons to `/etc/syslog-ng/config.yaml`:

```
volumes:
    - /path/to/your/config.yaml:/etc/syslog-ng/config.yaml

```

## Kubernetes:

The installation process is identical to the installation process for [Kubernetes for SC4S](./gettingstarted/k8s-microk8s.md) with the following modifications:

* Use the SC4S Lite image instead of SC4S in `values.yaml`:
```
image:
  repository: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

* Mount `config.yaml`. Add an `addons` section inside `sc4s` in `values.yaml`:

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

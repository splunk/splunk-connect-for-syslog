# Pluggable modules guide:

Pluggable modules **it's predefined modules**, that you can **only** *enable/disable* by changing config file.
After updating this config file with enabled addons you need to restart sc4s.

This config file it's a yaml file with list of addons ([whole list of addons here](https://github.com/splunk/splunk-connect-for-syslog/blob/main/package/lite/etc/config.yaml)):
```
---
addons:
    - cisco
    - paloalto
    - dell
```

You don't need to rebuild docker image, you **need mount custom config** into */etc/syslog-ng/config.yaml*.


## docker-compose:

1. [Read guide](./gettingstarted/docker-compose.md) how to use *docker-compose* for SC4S

2. Use *SC4S Lite image* instead of *SC4S* in docker-compose.yaml
```
image: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

3. *Mount config file* with addons to */etc/syslog-ng/config.yaml*:

```
volumes:
    - /path/to/your/config.yaml:/etc/syslog-ng/config.yaml
```



## k8s:

1. [Read guide](./gettingstarted/k8s-microk8s.md) how to use *k8s* for SC4S

2. Use *SC4S Lite image* instead of *SC4S*  in values.yaml:
```
image:
  repository: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

3. Mount config file. Add *addons* section on *sc4s* section of values.yaml:

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
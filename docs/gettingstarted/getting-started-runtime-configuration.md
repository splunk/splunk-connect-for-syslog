
# Implement a Container Runtime and SC4S

## Prerequisites

* Linux host with either Docker CE version 19.x or greater or Podman enabled, depending on your runtime choice.
* A network load balancer (NLB) configured to round-robin each HTTP POST request.

## Tune your reciever buffer
The host linux OS receiver buffer size must be tuned to match the SC4S default. This helps to avoid event dropping at the network level.
The default receiver buffer for SC4S is 16 MB for UDP traffic, which should be acceptable for most environments. To set the host OS kernel to
match this, edit `/etc/sysctl.conf` using the following whole-byte values corresponding to 16 MB:

```bash
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360
```
and apply to the kernel:
```bash
sysctl -p
```
* Verify that the kernel does not drop packets by periodically monitoring the buffer using the command
`netstat -su | grep "receive errors"`.
* Failure to tune the kernel for high-volume traffic results in message loss, which can be 
unpredictable and difficult to detect. See this helpful discussion in the syslog-ng
[Professional Edition](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-premium-edition/7.0.10/collecting-log-messages-from-udp-sources)
documentation regarding tuning syslog-ng in particular (via the [SC4S_SOURCE_*_SO_RCVBUFF](../configuration.md#syslog-source-configuration)
environment variable in SC4S) as well as overall host kernel tuning. The default values for receiver kernel buffers in most distrobutions is 2 MB,
which may not be adequate for your configuration. 

## Configure IPv4 forwarding

In many distributions, for example CentOS provisioned in AWS, IPv4 forwarding is not enabled by default.
IPv4 forwarding must be enabled for container networking. 
* To check that IPv4 forwarding is enabled:
```sudo sysctl net.ipv4.ip_forward```
* To enable IPv4 forwarding:
```sudo sysctl net.ipv4.ip_forward=1```

* To ensure your changes persist upon reboot: 
  * Define sysctl settings through files in ```/usr/lib/sysctl.d/```, ```/run/sysctl.d/```, and ```/etc/sysctl.d/```. 
  * To override only specific settings, either add a file with a lexically later name in ```/etc/sysctl.d/``` and put following setting there or find this specific setting in one of the  existing configuration files and set the value to ```1```.
```
net.ipv4.ip_forward=1
```

## Select a Container Runtime and SC4S Configuration

| Container Runtime and Orchestration                               | Operating Systems                                                                   |
|-------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| [MicroK8s](k8s-microk8s.md)                                       | Ubuntu with Microk8s                                                                |
| [Podman 1.7 & 1.9 + systemd](podman-systemd-general.md)           | RHEL 8.x or CentOS 8.x (best option), Debian or Ubuntu 18.04LTS                     |
| [Docker CE 19 (and greater) + systemd](docker-systemd-general.md) | RHEL or CentOS >7.7 (best option), Debian or Ubuntu 18.04LTS                        |
| [Docker Desktop + Compose](docker-compose-MacOS.md)               | MacOS                                                                               |
| [Docker Desktop + Compose](docker-compose.md)                     | RHEL or CentOS 8.1 & 8.2 (best option)                                              |
| [Bring your own Environment](byoe-rhel8.md)                       | RHEL or CentOS 8.1 & 8.2 (best option)                                              |
| [Offline Container Installation](docker-podman-offline.md)        | RHEL 8.x or CentOS 8.x (best option), Debian or Ubuntu 18.04LTS                     |
| [Ansible+Docker Swarm](ansible-docker-swarm.md)                   | RHEL 8.x or CentOS 8.x (best option), Debian or Ubuntu 18.04LTS                     |
| [Ansible+Podman](ansible-docker-swarm.md)                         | RHEL 7.x/8.x or CentOS 7.x/8.x (best option), Debian or Ubuntu 20.10LTS(and higher) |
| [Ansible+Docker](ansible-docker-swarm.md)                         | RHEL 7.x/8.x or CentOS 7.x/8.x (best option), Debian or Ubuntu 18.04LTS(and higher) |


### Create directories for your Docker or Podman configuration

Create the following three directories:
* `/opt/sc4s/local`: This directory is used as a mount point for local overrides and configurations. This empty `local` directory populates with defaults and examples at the first invocation
of SC4S for local configurations and context overrides. Do not change the directory structure of
these files, as SC4S depends on the directory layout
to read the local configurations properly. If necessary, you can change or add individual files. 
  * In the `local/config/` directory four subdirectories let you provide support for device types
that are not provided out of the box in SC4S. To get started, see the example log path template `lp-example.conf.tmpl`
and a filter `example.conf` in the `log_paths` and `filters` subdirectories.  Copy these as templates for your own log path development.
  * In the `local/context` directory, change the "non-example" version of a file (e.g. `splunk_metadata.csv`) to preserve the changes
upon restart.
* `/opt/sc4s/archive` is a mount point for local storage of syslog events
if the optional mount is uncommented. The events are written in the syslog-ng EWMM format. See the [Configuration](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/)
topic for information about the directory structure that the archive uses.

* `/opt/sc4s/tls` is a mount point for custom TLS certificates if the optional mount is uncommented.

  * When you create these directories, make sure that they match the volume mounts specified in the
sc4s.service [unit file](podman-systemd-general.md#unit-file). Failure to do this will cause SC4S to abort at startup.


#### Configure unique dedicated listening ports

You can dedicate a unique listening port to a specific source. You may need to do this because, for example, certain source technologies cannot categorize by message content, or because your configuration requires a unique listening port for certain devices.

To configure unique dedicated ports for one or more sources, modify the `/opt/sc4s/env_file` file to include the port-specific environment variable(s). See ["Sources"](../sources/index.md) to identify the specific environment variables that are mapped to each data source vendor or technology.

#### Modify index destinations for Splunk

Log paths are preconfigured to utilize a convention of index destinations that are suitable for most configuratons. To make changes to index destinations:
1. Navigate to `/opt/sc4s/local/context`.
2. Edit `splunk_metadata.csv` to review or change the index configuration for the data sources in your
environment. The key column uses the syntax `vendor_product`. Replace the index value in the third column of the
desired row with the index for your Splunk installation. See [Sources](https://splunk.github.io/splunk-connect-for-syslog/main/sources/vendor/AVI/document) for specific `vendor_product` keys
that pertain to the individual data source filters that are included with SC4S.
3. Splunk metadata such as source and sourcetype can also be overridden using this file. This is an advanced topic and is covered in the [Log Path overrides](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/) section of the Configuration topic.

#### Configure source filtering by source IP address or host name

You must configure legacy and non-standard-compliant sources by source IP or hostname as included in the event. To identify sources that require this step, see  ["Sources"](../sources/index.md).

#### Configure compliance index/metadata overrides

In some cases, devices that have been properly sourcetyped need to be further categorized by compliance, geography, or other criterion. You use the files `compliance_meta_by_source.conf` and `compliance_meta_by_source.csv` to do this.  The `conf` file specifies a filter to uniquely identify the messages that should be overridden, and the `csv` file
lists one or more metadata items that you can override based on the filter name. This is an advanced topic, see [Override index or metadata based on host, IP, or subnet]{https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#override-index-or-metadata-based-on-host-ip-or-subnet-compliance-overrides).

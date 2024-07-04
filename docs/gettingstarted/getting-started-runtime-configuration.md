
# Implement a Container Runtime and SC4S

## Step 1: Configure your OS to work with SC4S  
### Tune your receive buffer
You must tune the host Linux OS receive buffer size to match the SC4S default. This helps to avoid event dropping at the network level.
The default receive buffer for SC4S is 16 MB for UDP traffic, which should be acceptable for most environments. To set the host OS kernel to
match your buffer:

1. Edit `/etc/sysctl.conf` using the following whole-byte values corresponding to 16 MB:
```bash
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360
```

2. Apply to the kernel:
```bash
sysctl -p
```

3. To verify that the kernel does not drop packets, periodically monitor the buffer using the command
`netstat -su | grep "receive errors"`. Failure to tune the kernel for high-volume traffic results in message loss, which can be 
unpredictable and difficult to detect. The default values for receive kernel buffers in most distributions is 2 MB,
which may not be adequate for your configuration. 

### Configure IPv4 forwarding

In many distributions, for example CentOS provisioned in AWS, IPv4 forwarding is not enabled by default.
IPv4 forwarding must be enabled for container networking.

* To check that IPv4 forwarding is enabled: ```sudo sysctl net.ipv4.ip_forward```
* To enable IPv4 forwarding: ```sudo sysctl net.ipv4.ip_forward=1```
* To ensure your changes persist upon reboot: 
  * Define sysctl settings through files in ```/usr/lib/sysctl.d/```, ```/run/sysctl.d/```, and ```/etc/sysctl.d/```. 
  * To override only specific settings, either add a file with a lexically later name in ```/etc/sysctl.d/``` and put following setting there or find this specific setting in one of the  existing configuration files and set the value to ```1```.

```
net.ipv4.ip_forward=1
```

## Step 2: Create your local directory structure

Create the following three directories:

* `/opt/sc4s/local`: This directory is used as a mount point for local overrides and configurations. This empty `local` directory populates with defaults and examples at the first invocation of SC4S for local configurations and context overrides. Do not change the directory structure of these files, as SC4S depends on the directory layout to read the local configurations properly. If necessary, you can change or add individual files.
  * In the `local/config/` directory four subdirectories let you provide support for device types
that are not provided out of the box in SC4S. To get started, see the example log path template `lp-example.conf.tmpl`
and a filter `example.conf` in the `log_paths` and `filters` subdirectories.  Copy these as templates for your own log path development.
  * In the `local/context` directory, change the "non-example" version of a file (e.g. `splunk_metadata.csv`) to preserve the changes
upon restart.
* `/opt/sc4s/archive` is a mount point for local storage of syslog events
if the optional mount is uncommented. The events are written in the syslog-ng EWMM format. See the [Configuration](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/)
topic for information about the directory structure that the archive uses.
* `/opt/sc4s/tls` is a mount point for custom TLS certificates if the optional mount is uncommented.

When you create these directories, make sure that they match the volume mounts specified in the
sc4s.service [unit file](podman-systemd-general.md#unit-file). Failure to do this will cause SC4S to abort at startup.

## Step 3: Select a Container Runtime and SC4S Configuration

The table below shows possible ways to run SC4S using Docker/Podman with different management and orchestration systems.

Check your Podman or Docker documentation to see which operating systems are supported by your chosen container management tool. If the SC4S deployment model involves additional limitations or requirements regarding operating systems, you will find them in column "Additional Operating Systems Requirements".

| Container Runtime and Orchestration                               | Additional Operating Systems Requirements                                           |
|-------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| [MicroK8s](k8s-microk8s.md)                                       | Ubuntu with Microk8s                                                                |
| [Podman + systemd](podman-systemd-general.md)                     |                                                                                     |
| [Docker CE + systemd](docker-systemd-general.md)    |                                                                                                   |
| [Docker Desktop + Compose](docker-compose-MacOS.md)               | MacOS                                                                               |
| [Docker Compose](docker-compose.md)                               |                                                                                     |
| [Bring your own Environment](byoe-rhel8.md)                       | RHEL or CentOS 8.1 & 8.2 (best option)                                              |
| [Offline Container Installation](docker-podman-offline.md)        |                                                                                     |
| [Ansible+Docker Swarm](ansible-docker-swarm.md)                   |                                                                                     |
| [Ansible+Podman](ansible-docker-swarm.md)                         |                                                                                     |
| [Ansible+Docker](ansible-docker-swarm.md)                         |                                                                                     |

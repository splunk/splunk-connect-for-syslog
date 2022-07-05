
# Implement a Container Runtime and SC4S

## Prerequisites

* Linux host with Docker (CE 19.x or greater) or Podman enabled, depending on runtime choice (below).
* A network load balancer (NLB) configured for round-robin. Note: Special consideration may be required when more advanced products are used.
The optimal configuration of the load balancer will round-robin each http POST request (not each connection).
* The host linux OS receive buffer size should be tuned to match the sc4s default to avoid dropping events (packets) at the network level.
The default receive buffer for sc4s is set to 16 MB for UDP traffic, which should be OK for most environments.  To set the host OS kernel to
match this, edit `/etc/sysctl.conf` using the following whole-byte values corresponding to 16 MB:

```bash
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360
```
and apply to the kernel:
```bash
sysctl -p
```
* Ensure the kernel is not dropping packets by periodically monitoring the buffer with the command
`netstat -su | grep "receive errors"`.
* NOTE: Failure to account for high-volume traffic (especially UDP) by tuning the kernel will result in message loss, which can be _very_
unpredictable and difficult to detect. See this helpful discussion in the syslog-ng
[Professional Edition](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-premium-edition/7.0.10/collecting-log-messages-from-udp-sources)
documentation regarding tuning syslog-ng in particular (via the [SC4S_SOURCE_*_SO_RCVBUFF](../configuration.md#syslog-source-configuration)
environment variable in sc4s) as well as overall host kernel tuning.  The default values for receive kernel buffers in most distros is 2 MB,
which has proven inadequate for many.

## IPv4 Forwarding

In many distributions (e.g. CentOS provisioned in AWS), IPV4 forwarding is _not_ enabled by default.
This needs to be enabled for container networking to function properly.  The following is an example
to check and  set this up; as usual this needs to be vetted with your enterprise security policy:

To check:
```sudo sysctl net.ipv4.ip_forward```
To set:
```sudo sysctl net.ipv4.ip_forward=1```

To ensure the change survives a reboot: 
* sysctl settings are defined through files in ```/usr/lib/sysctl.d/```, ```/run/sysctl.d/```, and ```/etc/sysctl.d/```. 
* To override only specific settings, you can either add a file with a lexically later name in ```/etc/sysctl.d/``` and put following setting there:
```
net.ipv4.ip_forward=1
```
* or find this specific setting in one of existing configuration files (mentioned above) and set value to ```1```.

```
net.ipv4.ip_forward=1
```
## Select a Container Runtime and SC4S Configuration

| Container Runtime and Orchestration                               | Operating Systems                                               |
|-------------------------------------------------------------------|-----------------------------------------------------------------|
| [MicroK8s](k8s-microk8s.md)                                       | Ubuntu with Microk8s                                            |
| [Podman 1.7 & 1.9 + systemd](podman-systemd-general.md)           | RHEL 8.x or CentOS 8.x (best option), Debian or Ubuntu 18.04LTS |
| [Docker CE 19 (and greater) + systemd](docker-systemd-general.md) | RHEL or CentOS >7.7 (best option), Debian or Ubuntu 18.04LTS    |
| [Docker Desktop + Compose](docker-compose-MacOS.md)               | MacOS                                                           |
| [Bring your own Environment](byoe-rhel8.md)                       | RHEL or CentOS 8.1 & 8.2 (best option)                          |
| [Offline Container Installation](docker-podman-offline.md)        | RHEL 8.x or CentOS 8.x (best option), Debian or Ubuntu 18.04LTS |


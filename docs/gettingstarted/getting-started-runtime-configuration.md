
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

The table below shows possible ways to run SC4S using Docker/Podman with different management and orchestration systems.

Check your Podman or Docker documentation to see which operating systems are supported by your chosen container management tool. If the SC4S deployment model involves additional limitations or requirements regarding operating systems, you will find them in column "Additional Operating Systems Requirements".

| Container Runtime and Orchestration                               | Additional Operating Systems Requirements                                           |
|-------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| [MicroK8s](k8s-microk8s.md)                                       | Ubuntu with Microk8s                                                                |
| [Podman + systemd](podman-systemd-general.md)                     |                                                                                     |
| [Docker CE + systemd](docker-systemd-general.md)    |                                                                                     |
| [Docker Desktop + Compose](docker-compose-MacOS.md)               | MacOS                                                                               |
| [Docker Compose](docker-compose.md)                               |                                                                                     |
| [Bring your own Environment](byoe-rhel8.md)                       | RHEL or CentOS 8.1 & 8.2 (best option)                                              |
| [Offline Container Installation](docker-podman-offline.md)        |                                                                                     |
| [Ansible+Docker Swarm](ansible-docker-swarm.md)                   |                                                                                     |
| [Ansible+Podman \| Ansible+Docker](ansible-docker-swarm.md)       |                                                                                       |


### Docker and Podman basic configurations
* To run properly sc4s you need to create directories:`/opt/sc4s/local` `/opt/sc4s/archive` `/opt/sc4s/tls`
* `/opt/sc4s/local` will be used as a mount point for local overrides and configurations.
The empty `local` directory created above will populate with defaults and examples at the first invocation
of SC4S for local configurations and context overrides. _Do not_ change the directory structure of
the files that are laid down; change (or add) only individual files if desired.  SC4S depends on the directory layout
to read the local configurations properly.  See the notes below for which files will be preserved on restarts.
In the `local/config/` directory there are four subdirectories that allow you to provide support for device types
that are not provided out of the box in SC4S.  To get you started, there is an example log path template (`lp-example.conf.tmpl`)
and a filter (`example.conf`) in the `log_paths` and `filters` subdirectories, respectively.  These should _not_ be used directly,
but copied as templates for your own log path development.  They _will_ get overwritten at each SC4S start.  
In the `local/context` directory, if you change the "non-example" version of a file (e.g. `splunk_metadata.csv`) the changes
will be preserved on a restart.

* `/opt/sc4s/archive` will be used as a mount point for local storage of syslog events
(if the optional mount is uncommented above).  The events will be written in the syslog-ng EWMM format. See the "configuration"
document for details on the directory structure the archive uses.

* `/opt/sc4s/tls` will be used as a mount point for custom TLS certificates
(if the optional mount is uncommented above).

* IMPORTANT:  When creating the directories above, ensure the directories created match the volume mounts specified in the
sc4s.service [unit file](podman-systemd-general.md#unit-file).  Failure to do this will cause SC4S to abort at startup.


#### Dedicated (Unique) Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.
For collection of such sources, we provide a means of dedicating a unique listening port to a specific source.

Follow this step to configure unique ports for one or more sources:

* Modify the `/opt/sc4s/env_file` file to include the port-specific environment variable(s). Refer to the ["Sources"](../sources/index.md)
documentation to identify the specific environment variables that are mapped to each data source vendor/technology.

#### Modify index destinations for Splunk

Log paths are preconfigured to utilize a convention of index destinations that are suitable for most customers.

* If changes need to be made to index destinations, navigate to the `/opt/sc4s/local/context` directory to start.
* Edit `splunk_metadata.csv` to review or change the index configuration as required for the data sources utilized in your
environment. The key (1st column) in this file uses the syntax `vendor_product`.  Simply replace the index value (the 3rd column) in the
desired row with the index appropriate for your Splunk installation. The "Sources" document details the specific `vendor_product` keys (rows)
in this table that pertain to the individual data source filters that are included with SC4S.
* Other Splunk metadata (e.g. source and sourcetype) can be overridden via this file as well.  This is an advanced topic, and further
information is covered in the "Log Path overrides" section of the Configuration document.

#### Configure source filtering by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources that require this step, refer to the "sources" section of this documentation. See documentation
for your vendor/product to determine if specific configuration is required

#### Configure compliance index/metadata overrides

In some cases, devices that have been properly sourcetyped need to be further categorized by compliance, geography, or other criterion.
The two files `compliance_meta_by_source.conf` and `compliance_meta_by_source.csv` can be used for this purpose.  These operate similarly to
the files above, where the `conf` file specifies a filter to uniquely identify the messages that should be overridden, and the `csv` file
lists one or more metadata items that can be overridden based on the filter name.  This is an advanced topic, and further information is
covered in the "Override index or metadata based on host, ip, or subnet" section of the Configuration document.

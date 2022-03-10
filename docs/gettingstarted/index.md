# Before you start

## Getting Started

Splunk Connect for Syslog is a containerized distribution of syslog-ng with a configuration framework
designed to simplify getting syslog data into Splunk Enterprise and Splunk Cloud. Our approach is
to provide a runtime-agnostic solution allowing customers to deploy using the container runtime
environment of choice.


## Planning Deployment

Syslog is an overloaded term that refers to multiple message formats AND optionally a wire protocol for
transmission of events between computer systems over UDP, TCP, or TLS. The protocol is designed to minimize
overhead on the sender favoring performance over reliability. This fundamental choice means any instability
or resource constraint will cause data to be lost in transmission.

* When practical and cost effective (considering the importance of completeness as a requirement), place the sc4s
instance in the same VLAN as the source device.

* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* When High Availability of a single instance of SC4S is required, implement multi node clustering of the container
environment.
* Avoid TCP except where the source is unable to contain the event to a single UDP packet.
* Avoid TLS except where the event may cross a untrusted network.
* Plan for [appropriately sized hardware](../performance.md)


## Implementation

### Splunk Setup

#### Create Indexes

SC4S is pre-configured to map each sourcetype to a typical index. For new installations, it is best practice to create them in Splunk when
using the SC4S defaults. SC4S can be easily customized to use different indexes if desired.

* email
* epav
* epintel
* infraops
* netauth
* netdlp
* netdns
* netfw
* netids
* netlb
* netops
* netwaf
* netproxy
* netipam
* oswin
* oswinsec
* osnix
* print
* em_metrics (Optional opt-in for SC4S operational metrics; ensure this is created as a metrics index)

#### Install Related Splunk Apps

Install the following:

* [IT Essentials Work](https://splunkbase.splunk.com/app/5403/)

#### Configure the Splunk HTTP Event Collector

- Set up the Splunk HTTP Event Collector with the HEC endpoints behind a load balancer (VIP) configured for https round robin *WITHOUT* sticky
session.  Alternatively, a list of HEC endpoint URLs can be configured in SC4S (native syslog-ng load balancing) if no load balancer is in
place.  In most scenarios the recommendation is to use an external load balancer, as that makes longer term
maintenance simpler by eliminating the need to manually keep the list of HEC URLs specified in sc4s current. However, if a LB is not
available, native load balancing can be used with 10 or fewer Indexers where HEC is used exclusively for syslog.

  In either case, it is _strongly_ recommended that SC4S traffic be sent to HEC endpoints configured directly on the indexers rather than
an intermediate tier of HWFs.  
- Create a HEC token that will be used by SC4S and ensure the token has access to place events in main, em_metrics, and all indexes used as
event destinations.

* NOTE: It is recommended that the "Selected Indexes" on the token configuration page be left blank so that the token has access to
_all_ indexes, including the `lastChanceIndex`.  If this list is populated, extreme care must be taken to keep it up to date, as an attempt to
send data to an index not in this list will result in a `400` error from the HEC endpoint. Furthermore, the `lastChanceIndex` will _not_ be
consulted in the event the index specified in the event is not configured on Splunk.  Keep in mind just _one_ bad message will "taint" the
whole batch (by default 1000 events) and prevent the entire batch from being sent to Splunk.

- Refer to [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)
or [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q) for specific HEC configuration instructions based on your
Splunk type.

### Implement a Container Runtime and SC4S

#### Prerequisites

* Linux host with Docker (CE 19.x or greater with Docker Swarm) or Podman enabled, depending on runtime choice (below).
* A network load balancer (NLB) configured for round robin. Note: Special consideration may be required when more advanced products are used.
The optimal configuration of the load balancer will round robin each http POST request (not each connection).
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
unpredictable and difficult to detect. See this helpful discusion in the syslog-ng
[Professional Edition](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-premium-edition/7.0.10/collecting-log-messages-from-udp-sources)
documentation regarding tuning syslog-ng in particular (via the [SC4S_SOURCE_*_SO_RCVBUFF](../configuration.md#syslog-source-configuration)
environment variable in sc4s) as well as overall host kernel tuning.  The default values for receive kernel buffers in most distros is 2 MB,
which has proven inadequate for many.

#### IPv4 Forwarding

In many distributions (e.g. CentOS provisioned in AWS), IPV4 forwarding is _not_ enabled by default.
This needs to be enabled for container networking to function properly.  The following is an example
to set this up; as usual this needs to be vetted with your enterprise security policy:

```sudo sysctl net.ipv4.ip_forward=1```

To ensure the change survives a reboot edit /etc/sysctl.conf, find (or add) the text below, and uncomment as shown:

```
# Uncomment the next line to enable packet forwarding for IPv4
net.ipv4.ip_forward=1
```

#### Select a Container Runtime and SC4S Configuration

| Container Runtime and Orchestration | Operating Systems |
|-----------------------------|-------|
| [MicroK8s](k8s-microk8s.md) | Ubuntu with Microk8s |
| [Podman 1.7 & 1.9 + systemd](podman-systemd-general.md) | RHEL 8.x or CentOS 8.x (best option), Debian or Ubuntu 18.04LTS |
| [Docker CE 18 & 19 + systemd](docker-systemd-general.md) | RHEL or CentOS >7.7 (best option), Debian or Ubuntu 18.04LTS |
| [Docker CE 18 & 19 + Swarm](docker-swarm-general.md) | CentOS >7.7 (best option), Debian or Ubuntu 18.04LTS |
| [Docker CE 18 & 19 + Swarm](docker-swarm-rhel7.md) | RHEL 7.7 Deprecated |
| [Docker Desktop + Compose](docker-compose-MacOS.md) | MacOS |
| [Bring your own Envionment](byoe-rhel8.md) | RHEL or CentOS 8.1 & 8.2 (best option) |

### Offline Container Installation

Follow these instructions to "stage" SC4S by downloading the container so that it can be loaded "out of band" on a
host machine, such as an airgapped system, without internet connectivity.

* Download container image "oci_container.tgz" from our [Github Page](https://github.com/splunk/splunk-connect-for-syslog/releases).
The following example downloads v1.12; replace the URL with the latest release or pre-release version as desired.

```
sudo wget https://github.com/splunk/splunk-connect-for-syslog/releases/download/v1.12.0/oci_container.tar.gz
```

* Distribute the container to the airgapped host machine using an appropriate file transfer utility.
* Execute the following command, using docker or podman as appropriate

```
<podman or docker> load < oci_container.tar.gz
```

* Note the container ID of the resultant load

```
Loaded image: docker.pkg.github.com/splunk/splunk-connect-for-syslog/ci:90196f77f7525bc55b3b966b5fa1ce74861c0250
```

* Use the container ID to create a local label
```
<podman or docker> tag docker.pkg.github.com/splunk/splunk-connect-for-syslog/ci:90196f77f7525bc55b3b966b5fa1ce74861c0250 sc4slocal:latest
```

* Use this local label `sc4slocal:latest` in the relevant unit or yaml file to launch SC4S (see the runtime options
above) by setting the `SC4S_IMAGE` environment variable in the unit file (example below), or the relevant `image:` tag
if using Docker Compose/Swarm.  Using this label will cause the runtime to select the locally loaded image, and will not
attempt to obtain the container image via the internet.

```
Environment="SC4S_IMAGE=sc4slocal:latest"
```
* Remove the entry
```
ExecStartPre=/usr/bin/docker pull $SC4S_IMAGE
```
from the relevant unit file when using systemd, as an external connection to pull the container is no longer needed (or available).

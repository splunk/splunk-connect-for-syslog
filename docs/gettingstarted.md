# Getting Started

Splunk Connect for Syslog is a containerized distribution of syslog-ng with a configuration framework
designed to simplify getting syslog data into Splunk Enterprise and Splunk Cloud. Our approach is
to provide a container runtime agnostic solution allowing customers to follow our guidance or adapt the solution
to their enterprise container strategy.


# Planning Deployment

Syslog is an overloaded term that refers to multiple message formats AND optionally a wire protocol for
transmission of events between computer systems over UDP, TCP, or TLS. The protocol is designed to minimize
overhead on the sender favoring performance over reliability. This fundamental choice means any instability
or resource constraint will cause data to be lost in transmission.

* When practical and cost effective considering the importance of completeness as a requirement, place the scs
instance in the same VLAN as the source device.

* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* When High Availability of a single instance of SCS is required, implement multi node clustering of the container 
environment.
* Avoid TCP except where the source is unable to contain the event to a single UDP packet.
* Avoid TLS except where the event may cross a untrusted network.


# Implementation

## Setup indexes in Splunk

SCS is pre-configured to map each sourcetype to a typical index, for new installations best practice is to create the following
indexes in Splunk. The indexes can be customized easily if desired. If using defaults create the following indexes on Splunk:

* netauth
* netfw
* netids
* netops
* netproxy
* netipam
* em_metrics (ensure this is created as a metrics index)

## Install Related Splunk Apps

Install the following:

* [Splunk App for Infrastructure](https://splunkbase.splunk.com/app/3975/)
* [Splunk Add-on for Infrastructure](https://splunkbase.splunk.com/app/4217/)
* [Splunk Metrics Workspace](https://splunkbase.splunk.com/app/4192/) *NOTE Included in Splunk 7.3.0 and above* 

## Setup Splunk HTTP Event Collector

- Set up the Splunk HTTP Event Collector with the HEC endpoints behind a load balancer (VIP) configured for https round robin *WITHOUT* sticky session.  Alternatively, a list of HEC endpoint URLs can be configured in SC4S if no load balancer is in place.  In either case, it is recommended that SC4S traffic be sent to HEC endpoints configured directly on the indexers rather than an intermediate tier of HWFs.
- Create a HEC token that will be used by SCS and ensure the token has access to place events in main, em_metrics, and all indexes used as event destinations
 
### Splunk Cloud

Refer to [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)

### Splunk Enterprise

Refer to [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q)

## Implement a container run time and SCS

| Container and Orchestration | Notes |
|-----------------------------|-------|
| [Podman + systemd single node](gettingstarted/podman-systemd-general.md) | First choice for RedHat 7.x and 8.x, second choice for Debian and Ubuntu (packages provided via PPA) |
| [Docker CE + systemd single node](gettingstarted/docker-systemd-general.md) | First choice for Debian, Ubuntu, and CentOS distributions with limited existing docker experience |
| [Docker CE + Swarm single node](gettingstarted/docker-swarm-general.md) | Option for Debian, Ubuntu, and CentOS  desiring swarm orchestration |
| [Docker CE + Swarm single node RHEL 7.7](gettingstarted/docker-swarm-rhel7.md) | Option for RedHat 7.7 desiring swarm orchestration |

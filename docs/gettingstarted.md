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

* When practical and cost effective considering the importance of completeness as a requirement, place the SC4s
instance in the same VLAN as the source device.

* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* When High Availability of a single instance of SC4S is required, implement multi node clustering of the container 
environment.
* Avoid TCP except where the source is unable to contain the event to a single UDP packet.
* Avoid TLS except where the event may cross a untrusted network.


# Implementation

## Setup indexes in Splunk

SC4S is pre-configured to map each sourcetype to a typical index, for new installations best practice is to create the following
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
- Create a HEC token that will be used by SC4S and ensure the token has access to place events in main, em_metrics, and all indexes used as event destinations
 
### Splunk Cloud

Refer to [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)

### Splunk Enterprise

Refer to [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q)

## Implement a container run time and sc4s

| Container and Orchestration | Notes |
|-----------------------------|-------|
| [Podman + systemd single node](gettingstarted/podman-systemd-general.md) | First choice for RedHat 7.x and 8.x, second choice for Debian and Ubuntu (packages provided via PPA) |
| [Docker CE + systemd single node](gettingstarted/docker-systemd-general.md) | First choice for Debian, Ubuntu, and CentOS distributions with limited existing docker experience |
| [Docker CE + Swarm single node](gettingstarted/docker-swarm-general.md) | Option for Debian, Ubuntu, and CentOS  desiring swarm orchestration |
| [Docker CE + Swarm single node RHEL 7.7](gettingstarted/docker-swarm-rhel7.md) | Option for RedHat 7.7 desiring swarm orchestration |

# Pre-req

* Linux host with Docker 19.x or newer with Docker Swarm enabled
    * [Getting Started](https://docs.docker.com/get-started/)
* A Splunk index for metrics typically "em_metrics"
* One or more Splunk indexes for events collected by SC4S
* Splunk HTTP event collector enabled with a token dedicated for SC4S
    * [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q)
    * [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)
* A network load balancer (NLB) configured for round robin. Note: Special consideration may be required when more advanced products are used. The optimal configuration of the load balancer will round robin each http POST request (not each connection)


## Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations

![SC4S deployment diagram](SC4S%20deployment.png)


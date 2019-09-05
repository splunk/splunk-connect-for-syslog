# Getting Started

Splunk Connect for Syslog is a containerized distribution of syslog-ng with a configuration framework
designed to simplify getting syslog data into Splunk Enterprise and Splunk Enterprise Cloud. Our approach
to provide a container runtime agnostic solution allowing customers to follow our guidance or adapt the solution
to their enterprise container strategy.


# Planning Deployment

Syslog is an overloaded term that refers to multiple message formats AND optionally a wire protocol for
transmission of events between computer systems over UDP, TCP, or TLS. The protocol is designed to minimize
overhead on the sender favoring performance over reliability. This fundamental choice means any instability
or resource constraint will cause data to be lost in transmission.

* When practical and cost effective considering the importance of completeness as a requirement, place the scs
instance in the same VLAN as the source device

* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* When High Availability of a single instance of SCS is required do Implement multi node clustering of the container 
environment
* Avoid TCP except where the source is unable to contain the event to a single UDP packet
* Avoid TLS except where the event may cross a untrusted network


# Implementation

## Setup indexes in Splunk

SCS is pre-configured to map each sourcetype to a typical index, for new installations best practice is to create the following
indexes in Splunk. The indexes can be customized easily if desired. If using defaults create the following indexes on Splunk

* netauth
* netfw
* netids
* netops
* netproxy
* netipam
* em_metrics (Note this index is created by the )

## Install Related Splunk Apps

Install the following:

* [Splunk App for Infrastructure](https://splunkbase.splunk.com/app/3975/)
* [Splunk Add-on for Infrastructure](https://splunkbase.splunk.com/app/4217/)
* [Splunk Metrics Workspace](https://splunkbase.splunk.com/app/4192/) *NOTE Included in SPlunk 7.3.0 and above* 

## Setup Splunk HTTP Event Collector

- Setup Splunk HTTP Event Collector with a load balancer configured for https round robin *WITHOUT* sticky session.
- Create one or more tokens to be used by SCS, ensure the tokens have access to place events in main, em_metrics, and all indexes used as event destinations
 
### Splunk Enterprise Cloud

Refer to [Splunk Enterprise Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)

### Splunk Enterprise

Refer to [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q)

## Implement a container run time and SCS

| Container and Orchestration | Notes |
|-----------------------------|-------|
| [Docker + Swarm single node](gettingstarted/docker-swarm-general.md) | Applicable to operating systems supported by Docker CE  
| [Docker + Swarm single node RHEL 7.7](gettingstarted/docker-swarm-rhel7.md) | Community documented process for Docker CE on RHEL 7.7 |


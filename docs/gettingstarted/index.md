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

* When practical and cost-effective (considering the importance of completeness as a requirement), place the sc4s
instance in the same VLAN as the source device.

* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* When High Availability of a single instance of SC4S is required, implement multi node clustering of the container
environment.
* Avoid TCP except where the source is unable to contain the event to a single UDP packet.
* Avoid TLS except where the event may cross untrusted network.
* Plan for [appropriately sized hardware](../performance.md)


## Implementation

### [Splunk Setup](getting-started-splunk-setup.md)

### [Runtime configuration](getting-started-runtime-configuration.md)

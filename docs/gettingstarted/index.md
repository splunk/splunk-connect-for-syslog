# Before you start

## Getting Started

Splunk Connect for Syslog (SC4S) is a distribution of syslog-ng that simplifies getting your syslog data into Splunk Enterprise and Splunk Cloud. SC4S provides a runtime-agnostic solution that lets you deploy using the container runtime environment of choice and a configuration framework. This lets you process logs out-of-the-box from many popular devices and systems.


## Planning Deployment

Syslog can refer to multiple message formats as well as, optionally, a wire protocol for
event transmission between computer systems over UDP, TCP, or TLS. This protocol minimizes
overhead on the sender, favoring performance over reliability. This means any instability
or resource constraint can cause data to be lost in transmission.

* When practical and cost-effective, place the sc4s instance in the same VLAN as the source device.
* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* If you reguire high availability for a single instance of SC4S, implement multi-node clustering in the container
environment.
* Avoid TCP except where the source is unable to contain the event to a single UDP packet.
* Avoid TLS except where the event may cross an untrusted network.
* Plan for [appropriately sized hardware](../performance.md)


## Implementation

### [Splunk Setup](getting-started-splunk-setup.md)

### [Runtime configuration](getting-started-runtime-configuration.md)

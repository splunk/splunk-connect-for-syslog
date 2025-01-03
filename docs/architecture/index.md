# Architectural Considerations

Building a syslog ingestion architecture is complex and requires careful planning. The syslog protocol prioritizes speed and efficiency, often at the expense of resiliency and reliability. Due to these trade-offs, traditional scaling methods may not be directly applicable to syslog.

This document outlines recommended architectural solutions, along with alternative or unsupported methods that some users have found viable.

## Edge vs. centralized collection

While TCP and TLS are supported, UDP remains the dominant protocol for syslog transport in many data centers. Since syslog is a "send and forget" protocol, it performs poorly when routed through complex network infrastructures, including front-end load balancers and WAN.

The most reliable way to gather syslog traffic is through edge collection rather than centralized collection. When the syslog server is centrally located, UDP and stateless TCP traffic cannot adapt, leading to potential data loss.

Deploy SC4S instances in the same VLAN as the source devices.

## Avoid load balancing for syslog

Scale vertically by fine-tuning a single, robust server. Tools and methods for enhancing performance on your SC4S server are documented in:

1. [Fine-tune for TCP](tcp-optimization.md)
2. [Fine-tune for UDP](udp-optimization.md)

Avoid co-locating syslog-ng servers for horizontal scaling with load balancers. Load balancing challenges for horizontal scaling are described in the [Load Balancer's Overview](lb/index.md) section.

## High Availability (HA) considerations

Syslog is prone to data loss and can only achieve "mostly available" data collection.

### HA without load balancers

Load balancing does not work well with syslog’s stateless, unacknowledged traffic. Preserve more data by using simpler designs, such as vMotioned VMs.

The best deployment model for high availability is a [Microk8s](https://microk8s.io/) setup with MetalLB in BGP mode. This implements load balancing through destination network translation, providing better HA results.

## UDP vs. TCP

Syslog often uses UDP for log forwarding due to its low overhead and simplicity. UDP eliminates the need for network session establishment, which reduces network strain and avoids complex verification processes.

### Drawbacks of TCP

TCP uses acknowledgement signals (ACKS) to mitigate data loss. Issues may still arise, including:

- Events may be lost during TCP session establishment.
- Slow acknowledgment signals may lead to buffer overflows.
- Lost acknowledgments may cause closed connections.
- Data may be lost when the server restarts.

### When to use UDP vs. TCP

SC4S supports syslog ingestion via UDP, TCP/TLS, or a combination of both.

You can use UDP by default, but TCP is often preferable, for example for larger syslog events that exceed UDP packet limits, such as those from Web Proxy, DLP, or IDS sources.

The following resources can help you determine the best protocol for your setup:

1. [Run performance tests for TCP](performance-tests.md#check-your-tcp-performance)
2. [Run performance tests for UDP](performance-tests.md#check-your-udp-performance)

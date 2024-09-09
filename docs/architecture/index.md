# Architectural Considerations

Building a syslog ingestion architecture is complex and requires careful planning. The syslog protocol prioritizes speed and efficiency, often at the expense of resiliency and reliability. Due to these trade-offs, traditional scaling methods may not be directly applicable to syslog.

This document outlines recommended architectural solutions, along with alternative or unsupported methods that some users have found viable.

## Edge vs. Centralized Collection

While TCP and TLS are supported, UDP remains the dominant protocol for syslog transport in many data centers. Since syslog is a "send and forget" protocol, it performs poorly when routed through complex network infrastructures, including front-end load balancers and WAN.

### Recommendation: Use Edge Collection

The most reliable way to gather syslog traffic is through edge collection rather than centralized collection. If your syslog server is centrally located, UDP and stateless TCP traffic cannot adapt, leading to data loss.

## Avoid Load Balancing for Syslog

For optimal performance, scale vertically by fine-tuning a single, robust server. Key tools and methods for enhancing performance on your SC4S server are documented in:

1. [Fine-tune for TCP](tcp-optimization.md)
2. [Fine-tune for UDP](udp-optimization.md)

We advise against co-locating syslog-ng servers for horizontal scaling with load balancers. The challenges of load balancing for horizontal scaling are outlined in the [Load Balancer's Overview](lb/index.md) section.

## High Availability (HA) Considerations

Syslog, being prone to data loss, can only achieve "mostly available" data collection.

### HA Without Load Balancers

Load balancing does not suit syslog’s stateless, unacknowledged traffic. More data is preserved with simpler designs, such as vMotioned VMs.

The optimal deployment model for high availability uses a [Microk8s](https://microk8s.io/) setup with MetalLB in BGP mode. This method implements load balancing through destination network translation, providing better HA results.

## UDP vs. TCP

Syslog optimally uses UDP for log forwarding due to its low overhead and simplicity. UDP's streaming nature eliminates the need for network session establishment, which reduces network strain and avoids complex verification processes.

### Drawbacks of TCP

While TCP uses acknowledgement signals (ACKS) to mitigate data loss, issues still arise, such as:

- Loss of events during TCP session establishment
- Slow acknowledgment signals leading to buffer overflows
- Lost acknowledgments causing closed connections
- Data loss during server restarts

### When to Use UDP vs. TCP

Use UDP by default for syslog forwarding, switching to TCP for larger syslog events that exceed UDP packet limits (common with Web Proxy, DLP, and IDS sources).

The following resources will help you choose the best protocol for your setup:

1. [Run performance tests for TCP](performance-tests.md#check-your-tcp-performance)
2. [Run performance tests for UDP](performance-tests.md#check-your-udp-performance)
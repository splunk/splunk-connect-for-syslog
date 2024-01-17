# SC4S Architectural Considerations

Certain key architectural considerations provide performant and reliable syslog
data collection.  These
recommendations are not specific to Splunk Connect for Syslog, but rather stem from the syslog protocol and age.

## The syslog Protocol

The syslog protocol is designed for speed and efficiency at the
expense of resiliency and reliability.  UDP provides the ability to "send and forget" events over the network without regard
or acknowledgment of receipt. TLS/SSL are supported as well, though UDP still
tends to be the preferred syslog transport for most data centers.

Because of these tradeoffs selected by the original syslog designers and retained to this day, traditional methods to provide scale and
resiliency do not necessarily transfer to the syslog.  

## IP protocol

By default SC4S listens on ports using IPv4. IPv6 is also supported, for more information see `SC4S_IPV6_ENABLE` in [source configuration options](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#syslog-source-configuration).

## Collector Location

Since syslog is a "send and forget" protocol, it does not perform well when routed through substantial (and especially WAN) network infrastructure,
including front-side load balancers.  The most reliable way to collect syslog traffic is to provide for edge
collection rather than centralized collection.  Avoid centrally locating your syslog server, the UDP and (stateless)
TCP traffic cannot adjust for this and data loss will occur.

## syslog Data Collection at Scale
As a best practice, do not co-locate syslog-ng servers for horizontal scale and load balance to them with a front-side load balancer:

* Attempts to load balance for scale can cause more data loss due to normal device operations
and attendant buffer loss. A simple, robust single server (or shared-IP cluster) will provide better performance.

* Front-side load balancing will cause inadequate data distribution on the upstream side, leading to data unevenness on the indexers.

## High availability considerations and challenges

Load balancing for high availability does not work well for stateless, unacknowledged syslog traffic. More data will be lost than if you use a more simple design such as vMotioned VMs.  With syslog, the protocol itself is prone to loss, and there
will be data loss (similar to CD-quality (lossless) vs. MP3).  Syslog data collection can be made, at best, "Mostly Available".

## UDP vs. TCP

Run your syslog configuration on UDP rather than TCP.

The syslogd daemon was originally configured to use UDP for log forwarding to reduce overhead, as UDP's streaming method does not require the overhead of establishing a network session. 
UDP also reduces network load on the network stream with no required receipt verification or window adjustment.
Although TCP uses ACKS and there should not be data loss, loss cann occur when:

* The TCP session is closed: Events published while the system is creating a new session are lost. (Closed Window Case)
* The remote side is busy and can not ACK fast enough: Events are lost due to a full local buffer.
* A single ACK is lost by the network and the client closes the connection: Local and remote buffer are lost.
* The remote server restarts for any reason: Local buffer is lost.
* The remote server restarts without closing the connection: Local buffer plus timeout time are lost.
* The client side restarts without closing the connection
* Increased overhead on the network can lead to loss.
  
Use TCP if the syslog event is larger than the maximum size of the UDP packet on your network typically limited to Web Proxy, DLP, and IDs type sources.
To decrease drawbacks of TCP you can use TLS over TCP:

* The TLS can continue a session over a broken TCP reducing buffer loss conditions.
* The TLS will fill packets for more efficient use of wire.
* The TLS will compress in most cases.

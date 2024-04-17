# SC4S Architectural Considerations

SC4S provides performant and reliable syslog data collection.  When you are planning your configuration, review the following architectural considerations. These recommendations pertain to the Syslog protocol and age, and are not specific to Splunk Connect for Syslog.

## The syslog Protocol

The syslog protocol design prioritizes speed and efficiency, which can occur at the expense of resiliency and reliability.  User Data Protocol (UDP) provides the ability to "send and forget" events over the network without regard to or acknowledgment of receipt. Transport Layer Secuirty (TLS) and Secure Sockets Layer (SSL) protocols are also supported, though UDP prevails as the preferred syslog transport for most data centers.

Because of these tradeoffs, traditional methods to provide scale and resiliency do not necessarily transfer to syslog.  

## IP protocol

By default SC4S listens on ports using IPv4. IPv6 is also supported, for more information see `SC4S_IPV6_ENABLE` in [source configuration options](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#syslog-source-configuration).

## Collector Location

Since syslog is a "send and forget" protocol, it does not perform well when routed through substantial network infrastructure,
including front-side load balancers, and Particularly WAN.  The most reliable way to collect syslog traffic is to provide for edge
collection rather than centralized collection. If you centrally locate your syslog server, the UDP and (stateless)
TCP traffic cannot adjust and data loss will occur.

## syslog Data Collection at Scale
As a best practice, do not co-locate syslog-ng servers for horizontal scale and load balance to them with a front-side load balancer:

* Attempting to load balance for scale can cause more data loss due to normal device operations
and attendant buffer loss. A simple, robust single server or shared-IP cluster provides the best performance.

* Front-side load balancing causes inadequate data distribution on the upstream side, leading to data unevenness on the indexers.

## High availability considerations and challenges

Load balancing for high availability does not work well for stateless, unacknowledged syslog traffic. More data is preserved when you use a more simple design such as vMotioned VMs.  With syslog, the protocol itself is prone to loss, and Syslog data collection can be made, at best, "Mostly Available".

## UDP vs. TCP

Run your syslog configuration on UDP rather than TCP.

The syslogd daemon optimally uses UDP for log forwarding to reduce overhead. This is because UDP's streaming method does not require the overhead of establishing a network session. 
UDP also reduces network load on the network stream with no required receipt verification or window adjustment.

TCP uses Acknowledgement Signals (ACKS) to avoid data loss, however, loss can still occur when:

* The TCP session is closed: Events published while the system is creating a new session are lost. 
* The remote side is busy and cannot send an acknowledgement signal fast enough: Events are lost due to a full local buffer.
* A single acknowledgement signal is lost by the network and the client closes the connection: Local and remote buffer are lost.
* The remote server restarts for any reason: Local buffer is lost.
* The remote server restarts without closing the connection: Local buffer plus timeout time are lost.
* The client side restarts without closing the connection.
* Increased overhead on the network can lead to loss.
  
Use TCP if the syslog event is larger than the maximum size of the UDP packet on your network typically limited to Web Proxy, DLP, and IDs type sources.
To decrease drawbacks of TCP you can use TLS over TCP:

* The TLS can continue a session over a broken TCP, thereby reducing buffer loss conditions.
* The TLS fills packets for more efficient use of memory.
* The TLS compresses data in most cases.

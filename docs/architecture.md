# SC4S Architectural Considerations

There are some key architectural considerations and recommendations that will yield extremely performant and reliable syslog
data collection while minimizing the "over-engineering" that is common in many syslog data collection designs.  These
recommendations are not specific to Splunk Connect for Syslog, but rather stem from the syslog protocol itself -- and its age.

## The syslog Protocol

The syslog protocol was designed in the mid 1980s to offer very high-speed, network-based logging for network and security devices that
were (especially at the time) starved for CPU and I/O resources.  For this reason, the protocol was designed for speed and efficiency at the
expense of resiliency/reliability.  UDP was chosen due to its ability to "send and forget" the events over the network without regard
(or acknowledgment) of receipt.  In later years, TCP was added as a transport, as well as TLS/SSL.  In spite of these additions, UDP still
retains favor as a syslog transport for most data centers, and for the same reasons as originally designed.

Because of these tradeoffs selected by the original designers (and retained to this day), traditional methods used to provide scale and
resiliency do not necessarily transfer to the syslog world.  We will discuss (and reference) some of the salient points below.

## IP protocol

By default SC4S listens on ports using IPv4. IPv6 is also supported, see `SC4S_IPV6_ENABLE` in [source configuration options](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#syslog-source-configuration).

## Collector Location

Due to syslog being a "send and forget" protocol, it does not perform well when routed through substantial (and especially WAN) network infrastructure.
This _includes_ front-side load balancers.  The most reliable way to collect syslog traffic is to provide for _edge_
(not centralized) collection.  Resist the urge to centrally locate any syslog server (sc4s included) and expect the UDP and (stateless)
TCP traffic to "make it".  Data loss will undoubtedly occur.

## syslog Data Collection at Scale

In concert with attempts to centralize syslog, many admins will co-locate several syslog-ng servers for horizontal scale, and load balance
to them with a front-side load balancer.  For many reasons (that go beyond this short discussion) this is not a best practice.  Briefly:

* The attempt to load balance for scale (and HA -- see below) will actually cause _more_ data loss due to normal device operations
and attendant buffer loss than would be the case if a simple, robust single server (or shared-IP cluster) were used.

* Front-side load balancing will also cause inadequate data distribution on the upstream side, leading to data unevenness on the indexers.

## HA Considerations and Challenges

In addition to scale, many opt to load balance for high availability.  While a sound approach for stateful, application-level protocols such
as http, it does not work well for stateless, unacknowledged syslog traffic.  Again, in the attempt to design for HA, more data ends up
being lost vs. more simple designs such as vMotioned VMs.  With syslog, always remember that the protocol _itself_ is lossy, and there
_will_ be data loss (think CD-quality (lossless) vs. MP3).  Syslog data collection can be made, at best, "Mostly Available".

## UDP vs. TCP

For running syslog UDP is recommended over TCP.

The syslogd daemon was originally configured to use UDP for log forwarding to reduce overhead. 
While UDP is an unreliable protocol, it's streaming method does not require the overhead of establishing a network session. 
This protocol also reduces network load as the network stream with no required receipt verification or window adjustment.
While TCP could seem a better choice because it uses ACKS and there should not be data loss, there are some cases when it's possible:
* The TCP session is closed events published while the system is creating a new session will be lost. (Closed Window Case)
* The remote side is busy and can not ack fast enough events are lost due to local buffer full
* A single ack is lost by the network and the client closes the connection. (local and remote buffer lost)
* The remote server restarts for any reason (local buffer lost)
* The remote server restarts without closing the connection (local buffer plus timeout time lost)
* The client side restarts without closing the connection

Additionally as stated before it causes more overhead on the network.
TCP should be used in case of the syslog event is larger than the maximum size of the UDP packet on your network typically limited to Web Proxy, DLP and IDs type sources.
To decrease drawbacks of TCP you can use TLS over TCP:
* The TLS can continue a session over a broken TCP reducing buffer loss conditions
* The TLS will fill packets for more efficient use of wire
* The TLS will compress in most cases

# About using load balancers

Load balancers are not a best practice for SC4S. The exception to this is a narrow use case where the syslog server must be exposed to untrusted clients on the internet, such as with Palo Alto Cortex.

## Considerations

* UDP can only pass a load balancer using DNAT, and source IP must be preserved. If you use this configuration, the load balancer becomes a new single point of failure.
* TCP/TLS can use either a DNAT configuration or SNAT with "PROXY" Protocol enabled `SC4S_SOURCE_PROXYCONNECT=yes` (Experimental)
* TCP/TLS load balancers do not consider the weight of individual connection load and is frequently biased to one instance; all members in a single resource pool should be vertically scaled to accommodate the full workload.

## Alternatives

The best deployment model for high availability is a [Microk8s](https://microk8s.io/) based deployment with MetalLB in BGP mode. This model uses a special class of load balancer that is implemented as destination network translation.

# A word about load balancers

Customers often "require" the use of load balancers incorrectly attempting to meet a business requirement for availability. In general load balancers are not recommended with the exception of of a narrow use case where the Syslog Server must be exposed to untrusted clients on the internet such as Palo Alto Cortex.

## Considerations

* UDP MUST only pass a load balancer using DNAT. Source IP must be preserved. Note in this configuration a Load Balancer becomes a new single point of failure
* TCP/TLS May use a DNAT configuration OR SNAT with "PROXY" Protocol enabled `SC4S_SOURCE_PROXYCONNECT=yes` (Experimental)
* TCP/TLS load balancers do not consider the weight of individual connection load is frequently biased to one instance all members in a single resource pool should be vertically scaled to accommodate the full workload.

## Alternatives

The best deployment model for high availability is a Microk8s based deployment with MetalLB in BGP mode. This model uses a special class of load balancer that is implemented as destination network translation.
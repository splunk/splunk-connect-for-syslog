# Load Balancers Are Not a Best Practice for SC4S

The following issues may arise from load balancing syslog traffic:

- Load balancing for scale can lead to increased data loss due to normal device operations and buffer overflows.
- Front-side load balancing often results in uneven upstream data distribution.
- The default behavior of many load balancers is to overwrite the client's source IP with their own. Preserving the real source IP requires additional configuration.

### Best practices when using load balancers:
- Preserve the actual source IP of the sending device.
- Avoid using load balancers without High Availability (HA) mode.
- TCP/TLS load balancers may not account for the load on individual connections and might favor one instance over others. Ensure all members in a resource pool are vertically scaled to handle the full workload.

For **TCP**, you can use either a DNAT configuration or SNAT with the "PROXY" protocol enabled by setting `SC4S_SOURCE_PROXYCONNECT=yes`.  
For **UDP**, traffic can only pass through a load balancer using DNAT.

This section of the documentation discusses various load balancing solutions and example configurations, as well as known issues.

Please note that load balancing syslog traffic in front of SC4S is not supported by Splunk, and additional support from the load balancer vendor may be required.
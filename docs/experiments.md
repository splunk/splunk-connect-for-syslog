# Current experimental features

## > 3.12.0
`SC4S_USE_NAME_CACHE=yes` supports IPv6.

## > 3.0.0
### eBPF
eBPF is a feature that leverages Linux kernel infrastructure to evenly distribute the load, especially in cases when there is a huge stream of messages incoming from a single appliance.
To use the eBPF feature, you must have a host machine with and OS that supports eBPF. eBPF should be used only in cases when other ways of SC4S tuning fail. See the [instruction](./configuration.md#ebpf) for configuration details. 
To learn more visit this [blog post.](https://www.syslog-ng.com/community/b/blog/posts/syslog-ng-4-2-extra-udp-performance)

### Parallelize (TCP)
SC4S processes incoming messages from a TCP connection in a single thread. While this is adequate for many connections, it doesn't work efficiently when using a single or few high-traffic connections. This feature allows SC4S to process log messages from a single high-traffic TCP connection in multiple threads, which increases processing performance on multi-core machines.

To learn more, see the [Configuration documentation](./configuration.md#parallelize), as well as this [blog post](https://www.syslog-ng.com/community/b/blog/posts/accelerating-single-tcp-connections-in-syslog-ng-parallelize).

### SC4S Lite
In the new 3.0.0 update, we've introduced SC4S Lite. SC4S Lite is designed for those who prefer speed and custom filters over the pre-set ones that come with the standard SC4S. It's similar to our default version, without the pre-defined filters and complex app_parser topics. More information can be found at [dedicated page.](./lite.md)
## > 2.13.0
* In `env_file`, SC4S sets `SC4S_USE_NAME_CACHE=yes` to enable caching of the last valid host string, replaces nill, null, or IPv4 with the last good value, and stores this information in the `hostip.sqlite` file. 
    - Benefit: More correct host name values in Splunk when source vendor fails to provide valid syslog message.
    - Risk: Potential disk I/O usage and potential reduction in throughput when a high proportion of events are incomplete.
* To clear `hostip.sqlite` file, set `SC4S_CLEAR_NAME_CACHE=yes` flag in `env_file`. This action will automatically delete the `hostip.sqlite file` when SC4S restarts.
* In `env_file` set `SC4S_SOURCE_VMWARE_VSPHERE_GROUPMSG=yes` to enable additional post processing and merge multiline vmware events. You should also enable `SC4S_USE_NAME_CACHE=yes`, to accomodate event that have malformed or missing host names.
* In `env_file` set `SC4S_USE_VPS_CACHE=yes` to enable automatic configuration of `vendor_product` by source where possible. This feature caches `vendor` and `product` fields to determine of the best values for 
generic Linux events. For example, without this feature the "vendor product by host" app parser must be configured to identify ESX hosts so that ESX SSHD events can be routed using the meta key `vmware_vsphere_nix_syslog`. With this feature enabled a common event such as an event containing "program=vpxa" will cache this value. 
    - Benefit: Less config interaction
    - Risk: Potential disk I/O usage and potential reduction in throughput when a high proportion of events are incomplete.
    - Risk: misidentification due to load balancers and relay sources. 
* `SC4S_SOURCE_PROXYCONNECT=yes` for TCP and TLS connection expect "PROXY CONNECT" to provide the original client IP in SNAT load balancing.

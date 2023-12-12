# Current Experimental Features

### > 3.12.0
`SC4S_USE_NAME_CACHE=yes` supports IPv6.

### > 3.0.0
#### eBPF
eBPF is a feature that leverages Linux kernel infrastructure to evenly distribute the load especially in cases when there is a huge stream of messages incoming from a single appliance.
Prerequisite for using eBPF feature is a host machine with os that supports eBPF. It should be used only in cases when other ways of sc4s tuning are failing. Please refer to the [instruction](./configuration.md#ebpf) for configuration details. 
To learn more visit this [blog post.](https://www.syslog-ng.com/community/b/blog/posts/syslog-ng-4-2-extra-udp-performance)
#### SC4S Lite
In the new 3.0.0 update, we've introduced SC4S Lite. It's designed for those who prefer speed and custom filters over the pre-set ones that come with the standard SC4S. It's basically the same as our default version, minus the pre-defined filters and complex app_parser topics.More information can be found under [dedicated page.](./lite.md)
### > 2.13.0

* In env_file set `SC4S_USE_NAME_CACHE=yes` to enable caching last valid host string and replacing nill, null, or ipv4 with last good value and stores this information in the hostip.sqlite file. 
    - Benefit: More correct host name values in Splunk when source vendor fails to provide valid syslog message
    - Risk: Potential disk I/O usage (space, iops) Potential reduction in throughput when a high proportion of events are incomplete.
* To clear **hostip.sqlite** file, set `SC4S_CLEAR_NAME_CACHE=yes` flag in env_file. This action will automatically delete  the hostip.sqlite file when sc4s restarts.
* In env_file set `SC4S_SOURCE_VMWARE_VSPHERE_GROUPMSG=yes` To enable additional post processing to merge multiline vmware events. Recommend also enabling `SC4S_USE_NAME_CACHE=yes` as many events can be malformed or missing host name
* In env_file set `SC4S_USE_VPS_CACHE=yes` To enable automatic configuration of vendor_product by source where possible. This feature caches "vendor" and "product" fields from to use in determination of the best values for 
generic linux events for example without this feature the "vendor product by host" app parser must be configured to identify esx hosts so that esx SSHD events can be routed using the meta key `vmware_vsphere_nix_syslog` with this feature enabled a common event such containing "program=vpxa" will cache this value. 
    - Benefit: Less config interaction
    - Risk: Potential disk I/O usage (space, iops) Potential reduction in throughput when a high proportion of events are incomplete.
    - Risk: misidentification due to load balancers and relay sources. 
* `SC4S_SOURCE_PROXYCONNECT=yes` for TCP and TLS connection expect "PROXY CONNECT" to provide the original client IP in SNAT load balancing
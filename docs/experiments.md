# Current Experimental Features


# > 2.13.0

* In env_file set `SC4S_USE_NAME_CACHE=yes` to enable caching last valid host string and replacing nill, null, or ipv4 with last good value. 
    - Benefit: More correct host name values in Splunk when source vendor fails to provide valid syslog message
    - Risk: Potential disk I/O usage (space, iops) Potential reduction in throughput when a high proportion of events are incomplete.
* In env_file set `SC4S_SOURCE_VMWARE_VSPHERE_GROUPMSG=yes` To enable additional post processing to merge multiline vmware events. Recommend also enabling `SC4S_USE_NAME_CACHE=yes` as many events can be malformed or missing host name
* In env_file set `SC4S_USE_VPS_CACHE=yes` To enable automatic configuration of vendor_product by source where possible. This feature caches "vendor" and "product" fields from to use in determination of the best values for 
generic linux events for example without this feature the "vendor product by host" app parser must be configured to identify esx hosts so that esx SSHD events can be routed using the meta key `vmware_vsphere_nix_syslog` with this feature enabled a common event such containg "program=vpxa" will cache this value. 
    - Benefit: Less config interaction
    - Risk: Potential disk I/O usage (space, iops) Potential reduction in throughput when a high proportion of events are incomplete.
    - Risk: missidentification due to load balancers and relay sources. 


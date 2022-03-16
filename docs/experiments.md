# Current Experimental Features

# > 2.13.0

* In env_file set `SC4S_USE_NAME_CACHE=yes` to enable caching last valid host string and replacing nill, null, or ipv4 with last good value. 
    - Benefit: More correct host name values in Splunk when source vendor fails to provide valid syslog message
    - Risk: Potential disk I/O usage (space, iops) Potential reduction in throughput when a high proportion of events are incomplete.
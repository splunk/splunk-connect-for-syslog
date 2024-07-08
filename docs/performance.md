# Performance and Sizing
Performance testing against our lab configuration produces the following results and limitations. 

## Tested Configurations

### Splunk Cloud Noah
#### Environment

* Loggen (syslog-ng 3.25.1) - m5zn.3xlarge
* SC4S(2.30.0) + podman (4.0.2) - m5zn family
* SC4S_DEST_SPLUNK_HEC_DEFAULT_WORKERS=10 (default)
* Splunk Cloud Noah 8.2.2203.2 - 3SH + 3IDX

```bash
/opt/syslog-ng/bin/loggen -i --rate=100000 --interval=1800 -P -F --sdata="[test name=\"stress17\"]" -s 800 --active-connections=10 <local_hostmane> <sc4s_external_tcp514_port>
```
#### Result  

| SC4S instance | root networking                                                                                                     | slirp4netns networking                                                                                                |
|---------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| m5zn.large    | average rate = 21109.66 msg/sec, count=38023708, time=1801.25, (average) msg size=800, bandwidth=16491.92 kB/sec    | average rate = 20738.39 msg/sec, count=37344765, time=1800.75, (average) msg size=800, bandwidth=16201.87 kB/sec      |
| m5zn.xlarge   | average rate = 34820.94 msg/sec, count=62687563, time=1800.28, (average) msg size=800, bandwidth=27203.86 kB/sec    | average rate = 35329.28 msg/sec, count=63619825, time=1800.77, (average) msg size=800, bandwidth=27601.00 kB/sec      |
| m5zn.2xlarge  | average rate = 71929.91 msg/sec, count=129492418, time=1800.26, (average) msg size=800, bandwidth=56195.24 kB/sec   | average rate = 70894.84 msg/sec, count=127630166, time=1800.27, (average) msg size=800, bandwidth=55386.60 kB/sec     |
| m5zn.2xlarge  | average rate = 85419.09 msg/sec, count=153778825, time=1800.29, (average) msg size=800, bandwidth=66733.66 kB/sec   | average rate = 84733.71 msg/sec, count=152542466, time=1800.26, (average) msg size=800, bandwidth=66198.21 kB/sec     |




### Splunk Enterprise
#### Environment

* Loggen (syslog-ng 3.25.1) - m5zn.large
* SC4S(2.30.0) + podman (4.0.2) - m5zn family
* SC4S_DEST_SPLUNK_HEC_DEFAULT_WORKERS=10 (default)
* Splunk Enterprise 9.0.0 Standalone

```bash
/opt/syslog-ng/bin/loggen -i --rate=100000 --interval=600 -P -F --sdata="[test name=\"stress17\"]" -s 800 --active-connections=10 <local_hostmane> <sc4s_external_tcp514_port>
```
#### Result  

| SC4S instance | root networking                                                                                                                                                                                                                           | slirp4netns networking                                                                                                |
|---------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| m5zn.large    | average rate = 21511.69 msg/sec, count=12930565, time=601.095, (average) msg size=800, bandwidth=16806.01 kB/sec <br/> average rate = 21583.13 msg/sec, count=12973491, time=601.094, (average) msg size=800, bandwidth=16861.82 kB/sec   | average rate = 20738.39 msg/sec, count=37344765, time=1800.75, (average) msg size=800, bandwidth=16201.87 kB/sec      |
| m5zn.xlarge   | average rate = 37514.29 msg/sec, count=22530855, time=600.594, (average) msg size=800, bandwidth=29308.04 kB/sec <br/> average rate = 37549.86 msg/sec, count=22552210, time=600.594, (average) msg size=800, bandwidth=29335.83 kB/sec   | average rate = 35329.28 msg/sec, count=63619825, time=1800.77, (average) msg size=800, bandwidth=27601.00 kB/sec      |
| m5zn.2xlarge  | average rate = 98580.10 msg/sec, count=59157495, time=600.096, (average) msg size=800, bandwidth=77015.70 kB/sec <br/> average rate = 99463.10 msg/sec, count=59687310, time=600.095, (average) msg size=800, bandwidth=77705.55 kB/sec   | average rate = 84733.71 msg/sec, count=152542466, time=1800.26, (average) msg size=800, bandwidth=66198.21 kB/sec     |



## Guidance on sizing hardware

* Though vCPU (hyper threading) was used in these examples, syslog processing is a CPU-intensive task and resource oversubscription through sharing is not advised.
* The size of the instance must be larger than the absolute peak to prevent data loss; most sources cannot buffer during traffic congestion.
* CPU Speed is critical; slower or faster CPUs will impact throughput.
* Not all sources are equal in resource utilization. Well-formed Legacy BSD syslog messages were used in this test, but many sources are not syslog compliant and will require additional resources to process.


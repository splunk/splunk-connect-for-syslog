# Performance
Performance testing against our lab configuration produces the following results and limitations. 

## Tested Configuration

* SC4S instance requesting 8 cores and 4 GB of memory with K8S scheduler 
* 6 Splunk Indexers clustered in Single site
* 1 loggen test client using the following command:
    ```
    /opt/syslog-ng/bin/loggen -i --rate=1000 --interval=180 -P -F --sdata="[test name=\"stress17\"]" -s 800 --active-connections=10 sc4s 514`
    ```
* AWS instance type c5n.4xlarge

## Result  

The single syslog-ng container in this test is able to provide effective balancing and routing of events equivalent to 632 GB per day:

```
average rate = 9717.58 msg/sec, count=1749420, time=180.026, (average) msg size=800, bandwidth=7591.86 kB/sec
```


## Limitations

In our tests, if Splunk Enterprise’s implementation of the http event collection server responded to the client with a status code 200 and failed to commit the events to disk during a rolling restart, then 20-30 events per indexer were lost.

## Guidance on sizing hardware

The following reference deployment hardware specifications are based on Splunk performance testing results in Amazon Web Services. 
The overall load on your deployment hardware will vary based on the percentage of events not handled by a filter or use of 
exceptionally complex regex in filters. While we consider the following conservative, actual hardware performance will vary
due to network interface card, driver, kernel version, exact CPU, type of memory and configuration. SYSLOG is a fire 
and forget protocol making it sensitive to performance. Given this it is highly recommended that you validate 
performance with your hardware and production data samples. The syslog-ng loggen tool available in the SC4S container 
and the commands above can be utilized in this effort.

Deployment Size | Hardware Spec | Average EPS with average msg size 800 bytes
-- | -- | --
Small | 2 X 3.1 ghz cores1 GB of memory | 2K msg/sec
Medium | 4 X 3.1 ghz cores2 GB of memory | 4.5K msg/sec
Large | 8 X 3.1 ghz cores4 GB of memory | 9K msg/sec
XL | 16 X 3.1 ghz cores8 GB of memory | 18K msg/sec

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

Splunk Enterprise's implementation of the http event collection server responds to the client with a status code 200 and fails to commit the events to disk during a rolling restart. In our testing, 20-30 events per indexer are lost.


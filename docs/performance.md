# Performance

## Tested Configuration

* SC4S instance requesting 8 cores and 4 GB of memory with K8S scheduler. 
* 6 Splunk Indexers clustered in Single site
* 1 loggen test client using the following command 
* AWS instance type c5n.4xlarge

```bash
/opt/syslog-ng/bin/loggen -i --rate=1000 --interval=180 -P -F --sdata="[test name=\"stress17\"]" -s 800 --active-connections=10 sc4s 514
```

## Result  

The single syslog-ng container in this test is able to provided effective balancing and routing of events equivalent 632 GB per day 

```
average rate = 9717.58 msg/sec, count=1749420, time=180.026, (average) msg size=800, bandwidth=7591.86 kB/sec

```


## Limitations

* Splunk Enterprise's implementation of the http event collection server will respond to the client with a status code 200 and fail to commit the events to disk during a rolling restart in our testing 20-30 events per indexer pay be lost


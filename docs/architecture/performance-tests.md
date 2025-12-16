# Performance Tests

### Run your own performance tests
Your log ingestion system performance depends on several custom factors:

- Protocols (UDP/TCP/TLS).
- Network bandwidth between the source, syslog server, and backend.
- Number of Splunk indexers.
- Number and capacity of third-party SIEMs (alternative destinations).
- SC4S host's hardware specifications and software configurations.
- The number of syslog sources, the size of their logs, and whether they are well-formed and syslog compliant.
- Customizations.

Since actual performance heavily depends on these factors, the SC4S team cannot provide general estimates and you should conduct your own performance tests.

### When to run performance tests
- To estimate single-instance capacity. The size of the instance must be larger than the absolute anticipated input data peak to prevent data loss.
- To compare different hardware setups.
- To evaluate the impact of updating the SC4S configuration on performance.

### Install loggen
Loggen is a testing utility distributed with syslog-ng and is also available in SC4S.

#### Example: install loggen through syslog-ng
Refer to your syslog-ng documentation for installation instructions. For example, for Ubuntu:

```bash
wget -qO - https://ose-repo.syslog-ng.com/apt/syslog-ng-ose-pub.asc | sudo apt-key add -

# Update distribution name
echo "deb https://ose-repo.syslog-ng.com/apt/ stable ubuntu-noble" | sudo tee -a /etc/apt/sources.list.d/syslog-ng-ose.list

sudo apt-get update
sudo apt-get install syslog-ng-core
```

```bash
loggen -help
Usage:
  loggen [OPTION?]  target port
```

#### Example: use from your SC4S container
```bash
sudo podman exec -it SC4S bash
loggen --help
Usage:
  loggen [OPTION*]  target port
```

## Choose your hardware
Here is a reference example of performance testing using our lab configuration on various types of AWS EC2 machines.

### Tested configuration
* Loggen (syslog-ng 3.25.1) - m5zn.3xlarge
* SC4S(2.30.0) + podman (4.0.2) - m5zn family
* Splunk Cloud Noah 8.2.2203.2 - 3SH + 3IDX

### Command
```bash
/opt/syslog-ng/bin/loggen -i --rate=100000 --interval=1800 -P -F --sdata="[test name=\"stress17\"]" -s 800 --active-connections=10 <local_hostmane> <sc4s_external_tcp514_port>
```

!!! note "Note"
    Performance may vary depending on a version and specifics of your environment.

| SC4S instance | root networking                                                                                                     | slirp4netns networking                                                                                                |
|---------------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| m5zn.large    | average rate = 21109.66 msg/sec, count=38023708, time=1801.25, (average) msg size=800, bandwidth=16491.92 kB/sec    | average rate = 20738.39 msg/sec, count=37344765, time=1800.75, (average) msg size=800, bandwidth=16201.87 kB/sec      |
| m5zn.xlarge   | average rate = 34820.94 msg/sec, count=62687563, time=1800.28, (average) msg size=800, bandwidth=27203.86 kB/sec    | average rate = 35329.28 msg/sec, count=63619825, time=1800.77, (average) msg size=800, bandwidth=27601.00 kB/sec      |
| m5zn.2xlarge  | average rate = 71929.91 msg/sec, count=129492418, time=1800.26, (average) msg size=800, bandwidth=56195.24 kB/sec   | average rate = 70894.84 msg/sec, count=127630166, time=1800.27, (average) msg size=800, bandwidth=55386.60 kB/sec     |
| m5zn.2xlarge  | average rate = 85419.09 msg/sec, count=153778825, time=1800.29, (average) msg size=800, bandwidth=66733.66 kB/sec   | average rate = 84733.71 msg/sec, count=152542466, time=1800.26, (average) msg size=800, bandwidth=66198.21 kB/sec     |

## Watch out for queues
Comparing loggen results can be sufficient for A/B testing, but is not adequate for estimating the syslog ingestion throughput of the entire system.

In the following example, loggen was able to send 4.3 mln messages in one minute; however, Splunk indexers required an additional two minutes to process these messages. During that time, SC4S processed the messages and stored them in a queue while waiting for the HEC endpoint to accept new batches.

!!! note "Note"
    Performance may vary depending on a version and specifics of your environment.

| Splunk Indexers | Total Processing Time (4.3 mln messages) | Estimated Max EPS |
|-----------------|------------------------------------------|-------------------|
| 3               | 3 min                                    | 22K               |
| 30              | 1 min (no delay)                         | 72K               |

When running your tests, make sure to monitor the queues. The easiest way to do this is by accessing your server’s SC4S container and running:
```bash
watch "syslog-ng-ctl stats | grep '^dst.\+\(processed\|queued\|dropped\|written\)'"
```

If the destination is undersized or connections are slow, the number of queued events will increase, potentially reaching thousands or millions. Buffering is an effective solution for handling temporary data peaks, but constant input overflows will eventually fill up the buffers, leading to disk or memory issues or dropped messages. Ensure that you assess your SC4S capacity based on the number of messages that can be processed without putting undue pressure on the buffers.

## Check your TCP performance
Run the following command:
```
loggen --interval 60 --rate 120000 -s 800 --no-framing --inet --active-connections=10 <SC4S_IP> 514
```
Over a span of 60 seconds, loggen will establish 10 concurrent TCP connections to SC4S and attempt to generate up to 120,000 messages per second for each connection, with each message being 800 bytes in size. The more efficient the SC4S instance, the higher the average rate.

Example results:

* Loggen - c5.2xlarge
* SC4S(3.29.0) + podman - c5.4xlarge
* default configuration
* Splunk Cloud 9.2.2403.105 - 30IDX

!!! note "Note"
    Performance may vary depending on a version and specifics of your environment.

| Metric       | Default SC4S        | Finetuned SC4S      |
|--------------|---------------------|---------------------|
| Average Rate | 72,153.75 msg/sec   | 115,276.92 msg/sec  |

For more information, refer to [Finetune SC4S for TCP](tcp-optimization.md).

## Check your UDP performance
Run the following command:
```bash
loggen --interval 60 --rate 22000 -s 800 --no-framing --dgram <SC4S_IP> 514
```

Over a span of 60 seconds, loggen will attempt to generate 20,000 logs per second, each 800 bytes in size, which will be sent via UDP.

After running the command, count the number of events that reached Splunk. Since UDP is prone to data loss, messages can be lost anywhere along the path.

!!! note "Note"
    Performance may vary depending on a version and specifics of your environment.

| Receiver / Drops rate for EPS (msgs/sec) | 4,500  | 9,000  | 27,000 | 50,000 | 150,000 |
|------------------------------------------|--------|--------|--------|--------|---------|
| Default SC4S                             | 0.33%  | 1.24%  | 52.31% | 74.71% |    --   |
| Finetuned SC4S                           | 0%     | 0%     | 0%     | 0%     |  47.37% |

When running your tests, make sure to verify that Splunk indexed the total number of sent messages without delays.

In simple setups, where the source sends logs directly to the SC4S server, messages may be dropped from the port buffer. You can check the number of packets that encountered receive errors by running:
```bash
sudo netstat -ausn
```
The number of errors should match the number of missing messages in Splunk.

For more details on how to minimize message drops, refer to [Finetune SC4S for UDP](udp-optimization.md).
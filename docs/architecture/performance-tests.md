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

## Check your TCP performance
Run the following command:
```
loggen --interval 60 --rate 150000 -s 1000 --no-framing --inet --active-connections=10 <SC4S_IP> 514
```
Over a span of 60 seconds, loggen will establish 10 concurrent TCP connections to SC4S and attempt to generate up to 150,000 messages per second for each connection, with each message being 1000 bytes in size. The more efficient the SC4S instance, the higher the average rate.

Example results:

* Loggen - m5.4xlarge
* SC4S - m5.4xlarge
* Splunk Enterprise - m5.4xlarge single indexer

The *"Finetuned"* configuration for 1 active connection used the following settings:
```bash
SC4S_ENABLE_PARALLELIZE=yes
SC4S_PARALLELIZE_NO_PARTITION=16 # number of cores
```
The **SC4S_ENABLE_PARALLELIZE** setting does not increase performance when multiple TCP connections are used. For more information, refer to [Finetune SC4S for TCP](fine-tuning.md#finetune-for-tcp-traffic).

!!! note "Note"
    Performance may vary depending on a version and specifics of your environment.

| Metric       | Default SC4S - 1 connection | Defaults SC4S - 10 connections | Finetuned SC4S - 1 connection |
|--------------|-----------------------------|--------------------------------|-------------------------------|
| Average Rate | 12,393 msg/sec              | 68,240 msg/sec                 | 35,543 msg/sec                |


## Check your UDP performance
Run the following command:
```bash
loggen --interval 60 --rate 27000 -s 1000 --no-framing --dgram <SC4S_IP> 514
```

Over a span of 60 seconds, loggen will attempt to generate 27,000 messages per second, each 1,000 bytes in size, sent via UDP.

After running the command, count the number of events that reached Splunk. Since UDP is prone to data loss, messages can be lost anywhere along the path.

Example results:

* Loggen - m5.4xlarge
* SC4S - m5.4xlarge
* Splunk Enterprise - m5.4xlarge single indexer

The *"Finetuned"* configuration had eBPF enabled, an increased receive buffer, and an increased number of UDP sockets. However, for performance tests with a single data source and constant load, only the eBPF setting has an impact on performance. For more details, refer to [Finetune SC4S for UDP](fine-tuning.md#finetune-for-udp-traffic).

!!! note "Note"
    Performance may vary depending on a version and specifics of your environment.

| Receiver / Drops rate for EPS (msgs/sec) | 4,500 | 9,000 | 27,000 | 50,000 | 150,000 | 350,000 |
|------------------------------------------|-------|-------|--------|--------|---------|---------|
| Default SC4S                             | 0%    | 0%    | 59.4%  | 79.18% | 93.18%  | 96.88%  |
| Finetuned SC4S                           | 0%    | 0%    | 0%     | 0%     | 49.79%  | 81.10%  |

F
When running your tests, make sure to verify that Splunk indexed the total number of sent messages without delays.

In simple setups, where the source sends logs directly to the SC4S server, messages may be dropped from the port buffer. You can check the number of packets that encountered receive errors by running:
```bash
sudo netstat -ausn
```
The number of errors should match the number of missing messages in Splunk.

## Watch out for queues
Comparing loggen results can be sufficient for A/B testing, but is not adequate for estimating the syslog ingestion throughput of the entire system.

In the following example, loggen was able to send 4.3 million messages in one minute; however, Splunk indexers required an additional two minutes to process these messages. During that time, SC4S processed the messages and stored them in a queue while waiting for the HEC endpoint to accept new batches.

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
# Finetune SC4S for TCP Traffic
This section provides guidance on improving SC4S performance by tuning configuration settings.

### Tested configuration:
- **Loggen** - c5.2xlarge
- **SC4S** (3.29.0) + podman - c5.4xlarge
- **Splunk Cloud** 9.2.2403.105 - 30IDX

<small>Performance may vary depending on a version and specifics of your environment.</small>

| Setting                       | EPS (Events per Second) |
|-------------------------------|-------------------------|
| default                       | 71,327                  |
| SC4S_SOURCE_TCP_SO_RCVBUFF     | 99,207                  |
| SC4S_ENABLE_PARALLELIZE        | 101,700                 |
| SC4S_SOURCE_TCP_IW_USE         | 115,276                 |

You can apply these settings to your infrastructure to improve SC4S performance. After making adjustments, run the [performance tests](performance-tests.md#check-your-tcp-performance) and retain the changes that result in performance improvements.

## General fine-tuning patterns

### Disabling some of the features

Some of the features in sc4s may have a negative impact on the performance. In the scneario where there are problems with performance it is advised to disable some of the settings like **name cache** and **message grouping**:

```bash
SC4S_USE_NAME_CACHE=no
SC4S_SOURCE_VMWARE_VSPHERE_GROUPMSG=no
```

### Dedicated sc4s instances

If one of the logs sources produces a large percentage of the overall traffic, it is advised to create an additional dedicated sc4s service on a seperate host.

## Tune the receiving buffer

Increasing the TCP receive buffer allows the kernel to queue more incoming data before the application processes it, reducing packet loss during traffic bursts. This requires changes at both the OS level and within SC4S.

### Step 1: Increase the kernel buffer OS limits

Edit `/etc/sysctl.conf` and set the receive buffer size to 512 MB:

```bash
net.core.rmem_default = 536870912
net.core.rmem_max = 536870912
```

Apply the changes:

```bash
sudo sysctl -p
```

### Step 2: Configure SC4S to use the larger buffer

Add the following line to `/opt/sc4s/env_file`:

```bash
SC4S_SOURCE_TCP_SO_RCVBUFF=536870912
```

### Step 3: Restart SC4S

Restart SC4S for the changes to take effect.

### Other Protocols

If you use other syslog transports in addition to TCP, apply the same buffer tuning to each protocol you have enabled:

```bash
SC4S_SOURCE_TCP_SO_RCVBUFF=536870912       # Generic syslog over TCP
SC4S_SOURCE_UDP_SO_RCVBUFF=536870912       # Generic syslog over UDP
SC4S_SOURCE_RFC5426_SO_RCVBUFF=536870912   # RFC 5426 (syslog over UDP)
SC4S_SOURCE_RFC6587_SO_RCVBUFF=536870912   # RFC 6587 (syslog over TCP)
SC4S_SOURCE_RFC5425_SO_RCVBUFF=536870912   # RFC 5425 (syslog over TLS)
```

### Additional considerations

- **Sending buffer:** In rare cases, you may also need to increase the sending buffer size by modifying `net.core.wmem_max` and `net.core.wmem_default` using the same approach.
- **Buffer size limits:** Setting buffers too large can actually decrease performance. Start with the recommended values and adjust based on your testing results.
- **Hardware constraints:** Network driver limitations should be considered when tuning these values. Consult your NIC documentation for maximum supported buffer sizes.

## Tune static input window size

Input window provides flow‑control at the application level. Syslog‑ng uses this feature to temporarily buffer messages when outputs are slow. The mechanism works by pulling messages from the kernel’s receive buffer and placing them into an application buffer.

- The window size defines how many messages this internal buffer can hold.
- Each message fetched from the kernel buffer increases the window counter.
- Each message successfully forwarded to the output decreases the counter.

To change the window size, modify following option in `/opt/sc4s/env_file`:

```bash
SC4S_SOURCE_TCP_IW_SIZE=1000000
```

In the example above, the input window can store up to **100,000 messages**. Note that increasing the window size will increase the application's memory usage.

### Fetch limit

When increasing the input window size, you may also need to increase the **fetch limit**. The fetch limit controls the maximum number of messages retrieved from the source in a single read operation.

- **Too high**: Should not exceed the input window size, as this would fill the entire buffer in one read cycle.
- **Too low**: Results in underutilizing the buffer capacity, requiring more read cycles to process the same volume.

The default value is `1000`.

## Disk Buffering

To prevent message loss during HEC connection outages, consider enabling [Disk Buffering](../configuration.md#configure-your-sc4s-disk-buffer). This feature temporarily stores messages on disk when the destination is unavailable.

## Parallelize TCP processing
1. Update `/opt/sc4s/env_file` and restart SC4S.
```
SC4S_ENABLE_PARALLELIZE=yes
SC4S_PARALLELIZE_NO_PARTITION=4
```

Parallelize distributes messages from a single TCP stream across multiple concurrent threads, which is noticeable in production environments with a single high-volume TCP source.

| SC4S Parallelize    | Loggen TCP Connections         | %Cpu(s) us | Average Rate (msg/sec) |
|---------------------|--------------------------------|------------|------------------------|
| off                 | 1                              |     9.0    |         14,144.10      |
| off                 | 10                             |    59.3    |         73,743.32      |
| on (10 threads)     | 1                              |    58.4    |         77,842.18      |


## Switch to SC4S Lite
Parsing syslog messages can be a CPU-intensive task. During the parsing process, each syslog message goes through multiple parsing rules until a match is found. Some log messages follow longer parsing paths than others, and some parsers use regular expressions, which can be slow.

If you are familiar with your log sources, consider performing an A/B test and switching to SC4S Lite, which includes only the parsers for the vendors you require. Although artificial performance tests may not fully reflect the impact of this change, you may observe an increase in the capacity of your syslog layer when operating with real-world data.


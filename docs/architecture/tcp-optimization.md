# Finetune SC4S for TCP Traffic
This section provides guidance on improving SC4S performance by tuning configuration settings.

### Tested configuration:
- **Loggen** - c5.2xlarge
- **SC4S** (3.29.0) + podman - c5.4xlarge
- **Splunk Cloud** 9.2.2403.105 - 30IDX

| Setting                       | EPS (Events per Second) |
|-------------------------------|-------------------------|
| default                       | 71,327                  |
| SC4S_SOURCE_TCP_SO_RCVBUFF     | 99,207                  |
| SC4S_ENABLE_PARALLELIZE        | 101,700                 |
| SC4S_SOURCE_TCP_IW_USE         | 115,276                 |

You can apply these settings to your infrastructure to improve SC4S performance. After making adjustments, run the [performance tests](performance-tests.md#check-your-tcp-performance) and retain the changes that result in performance improvements.

## Tune your receiving buffer
1. Update `/etc/sysctl.conf`

From default buffer size:
```
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360
```

to 512MB:
```
net.core.rmem_default = 536870912
net.core.rmem_max = 536870912
```

And apply changes:
```
sudo sysctl -p
```

2. Update `/opt/sc4s/env_file`  
```
SC4S_SOURCE_TCP_SO_RCVBUFF=536870912
```

3. Restart SC4S

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

## Tune static window size
1. Update `/opt/sc4s/env_file` and restart SC4S.
```
SC4S_SOURCE_TCP_IW_USE=yes
SC4S_SOURCE_TCP_IW_SIZE=1000000
```

## Switch to SC4S Lite
Parsing syslog messages can be a CPU-intensive task. During the parsing process, each syslog message goes through multiple parsing rules until a match is found. Some log messages follow longer parsing paths than others, and some parsers use regular expressions, which can be slow.

If you are familiar with your log sources, consider performing an A/B test and switching to SC4S Lite, which includes only the parsers for the vendors you require. Although artificial performance tests may not fully reflect the impact of this change, you may observe an increase in the capacity of your syslog layer when operating with real-world data.


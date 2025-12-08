# Finetune SC4S for UDP Traffic
This section demonstrates how SC4S can be vertically scaled by adjusting configuration parameters to significantly reduce UDP packet drops.

### Tested configuration:
- **Loggen** - c5.2xlarge
- **SC4S** (3.29.0) + podman - c5.4xlarge
- **Splunk Cloud** 9.2.2403.105 - 30IDX

<small>Performance may vary depending on a version and specifics of your environment.</small>

| Setup for 67,000 EPS (Events per Second) | % Loss |
|------------------------------------------|--------|
| Default                                  | 77.88  |
| OS Kernel Tuning                         | 24.38  |
| Increasing the Number of UDP Sockets     | 22.95  |
| eBPF                                     | 0      |

Consider applying these changes to your infrastructure. After each adjustment, run the [performance tests](performance-tests.md#check-your-udp-performance) and retain the changes that result in improvements.

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
SC4S_SOURCE_UDP_SO_RCVBUFF=536870912
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

## Flow-control with static input window size

Input window provides flow‑control at the application level. Syslog‑ng uses this feature to temporarily buffer messages when outputs are slow. The mechanism works by pulling messages from the kernel’s receive buffer and placing them into an application buffer.

- The window size defines how many messages this internal buffer can hold.
- Each message fetched from the kernel buffer increases the window counter.
- Each message successfully forwarded to the output decreases the counter.

To enable it, set the following options in `/opt/sc4s/env_file`:

```bash
SC4S_SOURCE_UDP_IW_USE=yes 
SC4S_SOURCE_TCP_IW_SIZE=250000
```

In the example above, the input window can store up to **250,000 messages**. If the output becomes slow and this window fills up, syslog‑ng will stop reading from the kernel buffer. As a result, the kernel buffer will begin to fill, and once it becomes full, **incoming UDP packets will be dropped** by the kernel.

A single UDP message can be up to approximately 1 KB. With a window size of 250,000 messages, this may require up to **250 MB** of additional memory for buffering.

### Fetch limit

When increasing the input window size, you may also need to increase the **fetch limit**. The fetch limit controls the maximum number of messages retrieved from the source in a single read operation.

- **Too high**: Should not exceed the input window size, as this would fill the entire buffer in one read cycle.
- **Too low**: Results in underutilizing the buffer capacity, requiring more read cycles to process the same volume.

The default value is `1000`.

## Increase the number of UDP sockets

By default, SC4S uses a single UDP socket per port. Increasing the number of sockets allows traffic to be distributed across multiple CPU threads using the kernel's `SO_REUSEPORT` feature.

### Default behavior (without eBPF)

The kernel assigns packets to sockets based on a hash of the source IP and port. This means:

- **Consistent routing**: All packets from the same sender go to the same socket, preserving message order.
- **Potential imbalance**: If a few senders generate most of the traffic, their packets may all land on the same socket, leaving other sockets underutilized.

### With eBPF enabled

eBPF provides true per-packet load balancing, where each packet is randomly distributed across all sockets regardless of sender. This results in:

- **Even workload**: Traffic is distributed more uniformly across CPU threads.
- **No ordering guarantee**: Packets from the same sender may be processed out of order.

### Configuration

Add the following to `/opt/sc4s/env_file`:

```bash
SC4S_SOURCE_LISTEN_UDP_SOCKETS=32
```

Set this value based on the number of CPU cores available. Start with a value equal to your 4 x core count and adjust based on performance testing.

## Enable eBPF

Find more in the [About eBPF](../../configuration/#about-ebpf) section.

1. Verify that your host supports eBPF. 
2. Ensure your container is running in privileged mode. 
3. Update the configuration in `/opt/sc4s/env_file`:
```bash
SC4S_SOURCE_LISTEN_UDP_SOCKETS=32
SC4S_ENABLE_EBPF=yes
SC4S_EBPF_NO_SOCKETS=32
```
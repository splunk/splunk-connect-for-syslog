# SC4S Configuration Tool

The SC4S Configuration Tool is an interactive shell script that generates an optimized `env_file` for Splunk Connect for Syslog. Instead of manually editing environment variables, you answer a series of prompts and the tool produces a ready-to-deploy configuration file.

## Prerequisites

- A running shell environment (bash or sh)
- Your need to know your Splunk HEC URL and token

## Quick start

Run the tool from the root of the SC4S repository:

```bash
sh ./configuration-tool.sh
```

The tool walks you through each configuration section and writes the result to an `env_file` (or a filename you choose). A review step is shown before anything is written to disk.

## Command-line options

| Option | Description |
|---|---|
| `-h`, `--help` | Show help message |
| `-o`, `--output` | Set the output filename (default: `env_file`) |

Example:

```bash
sh ./configuration-tool.sh -o my_sc4s_config
```

## Configuration modes

### Mode 1: Custom configuration

Step-by-step interactive mode where you control every setting. This is the default when you run the tool.

The tool prompts you through the following sections in order:

1. **Splunk HEC** &mdash; URL, token, and TLS verification
2. **Protocol selection** &mdash; UDP only, TCP only, or both
3. **Advanced UDP options** &mdash; fetch limit, listen sockets, receive buffer, eBPF, window size
4. **Advanced TCP options** &mdash; receive buffer, parallelization, window size
5. **Disk buffer** &mdash; enable/disable, reliable vs normal mode, memory and disk buffer sizes

### Mode 2: Hardware-based configuration

Auto-tuned mode that selects performance settings based on your hardware profile and expected events per second (EPS). You only need to provide:

1. **Hardware profile** &mdash; select the instance type closest to your environment
2. **Expected EPS** &mdash; your anticipated event throughput
3. **Protocol** &mdash; UDP, TCP, or both
4. **Splunk HEC** &mdash; URL, token, and TLS verification

The tool applies optimized defaults based on these inputs. See [Hardware profiles](#hardware-profiles) for the available profiles and their thresholds.

## Configuration sections

### Splunk HEC

| Setting | Description | Example |
|---|---|---|
| HEC URL | The URL of your Splunk HTTP Event Collector endpoint | `https://splunk.example.com:8088` |
| HEC Token | A valid HEC token in UUID format | `00000000-0000-0000-0000-000000000000` |
| TLS Verify | Whether to verify SSL/TLS certificates (default: yes) | `yes` or `no` |

Both the URL and token are validated before proceeding.

### Protocol selection

| Option | Description |
|---|---|
| UDP only | Faster throughput, but messages may be lost under heavy load |
| TCP only | Reliable delivery with guaranteed ordering |
| Both | Optimize for both UDP and TCP |

Choose based on your data sources and reliability requirements. See [Protocol selection guidance](index.md/#udp-vs-tcp) for help deciding.

### Advanced UDP options

These options appear when UDP is selected (either "UDP only" or "Both").

| Setting | Environment variable | Default | Description |
|---|---|---|---|
| Fetch limit | `SC4S_SOURCE_UDP_FETCH_LIMIT` | 1000 | Number of messages fetched per poll cycle. Increase for high-throughput scenarios |
| Listen sockets | `SC4S_SOURCE_LISTEN_UDP_SOCKETS` | 2 | Number of UDP listen sockets. More sockets can improve throughput on multi-core systems |
| Receive buffer | `SC4S_SOURCE_UDP_SO_RCVBUFF` | -1 (skip) | OS-level UDP receive buffer size in bytes. Set to -1 to use system defaults |
| eBPF | `SC4S_ENABLE_EBPF` | no | Enable eBPF-based load balancing across sockets for high-volume UDP |
| eBPF sockets | `SC4S_EBPF_NO_SOCKETS` | 4 | Number of eBPF sockets (only when eBPF is enabled) |
| Window size | `SC4S_SOURCE_UDP_IW_SIZE` | 1000000 | Static input window size for UDP (only when tuning is enabled) |

!!! note
    If you configure a custom receive buffer, you must also adjust your OS kernel settings. The tool prints the required `sysctl` commands after generating the configuration. See [Tune the receiving buffer](fine-tuning.md#tune-the-receiving-buffer) for details.

!!! note
    Enabling eBPF requires additional system permissions. Ensure your system supports eBPF and the necessary capabilities are granted. See [About eBPF](../configuration.md#about-ebpf) for details.

### Advanced TCP options

These options appear when TCP is selected (either "TCP only" or "Both").

| Setting | Environment variable | Default | Description |
|---|---|---|---|
| Receive buffer | `SC4S_SOURCE_TCP_SO_RCVBUFF` | -1 (skip) | OS-level TCP receive buffer size in bytes. Set to -1 to use system defaults |
| Parallelization | `SC4S_ENABLE_PARALLELIZE` | no | Enable parallel processing of TCP connections across partitions |
| Partitions | `SC4S_PARALLELIZE_NO_PARTITION` | 4 | Number of partitions for parallel processing (only when parallelization is enabled) |
| Window size | `SC4S_SOURCE_TCP_IW_SIZE` | 1000000 | Static input window size for TCP (only when tuning is enabled) |

### Disk buffer

Disk buffering provides local storage to prevent data loss when the Splunk destination is temporarily unavailable.

| Setting | Environment variable | Default | Description |
|---|---|---|---|
| Enable | `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE` | yes | Enable local disk buffering |
| Reliable mode | `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE` | no | Use reliable disk buffering (slower but safer). Normal mode is recommended for most deployments |
| Memory buffer size | `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE` | 10241024 | Worker memory buffer size in bytes (reliable mode) |
| Memory buffer length | `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH` | 15000 | Worker memory buffer size in message count (normal mode) |
| Disk buffer size | `SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE` | 53687091200 (~50 GB) | Maximum disk buffer size per worker in bytes |

## Hardware profiles

When using hardware-based configuration mode, the tool maps your hardware and EPS to optimized settings. The following table shows when performance tuning is automatically applied.

### 16 vCPUs, 64 GB RAM (for example, AWS m5.4xlarge)

| Protocol | EPS threshold | Applied settings |
|---|---|---|
| UDP | > 35,000 | Fetch limit 1M, eBPF with 16 sockets, 64 listen sockets, 512 MB receive buffer |
| TCP | > 50,000 | Parallelization with 8 partitions, 512 MB receive buffer |

### 8 vCPUs, 32 GB RAM (for example, AWS m5.2xlarge)

| Protocol | EPS threshold | Applied settings |
|---|---|---|
| UDP | > 25,000 | Fetch limit 1M, eBPF with 16 sockets, 32 listen sockets, 256 MB receive buffer |
| TCP | > 30,000 | Parallelization with 8 partitions, 256 MB receive buffer |

### 4 vCPUs, 16 GB RAM (for example, AWS m5.xlarge)

| Protocol | EPS threshold | Applied settings |
|---|---|---|
| UDP | > 10,000 | Fetch limit 1M, eBPF with 8 sockets, 16 listen sockets, 256 MB receive buffer |
| TCP | > 20,000 | Parallelization with 4 partitions, 256 MB receive buffer |

If your EPS is below the threshold for your hardware profile, default settings are used and no additional tuning is applied.

## Output

The tool generates an `env_file` with contents similar to:

```bash
# SC4S Configuration - Generated by configuration tool
# Mode: Hardware-based (8vCPUs)
# Expected EPS: 30000
# Protocol: udp
# Generated on: Thu Mar 5 12:00:00 UTC 2026

# === Splunk HEC Configuration ===
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://splunk.example.com:8088
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=12345678-1234-1234-1234-123456789abc

# === Performance Configuration ===
SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
SC4S_SOURCE_LISTEN_UDP_SOCKETS=32
SC4S_SOURCE_UDP_SO_RCVBUFF=268435456
SC4S_ENABLE_EBPF=yes
SC4S_EBPF_NO_SOCKETS=16
```

Before writing, the tool displays the full configuration for review and asks for confirmation.

## Post-configuration steps

After generating your `env_file`:

1. **Copy the file** to your SC4S deployment directory (typically `/opt/sc4s/env_file`).

2. **Adjust kernel buffers** if you configured a custom receive buffer. The tool prints the exact `sysctl` settings needed. For example:

    ```bash
    # Add to /etc/sysctl.conf
    net.core.rmem_default = 268435456
    net.core.rmem_max = 268435456

    # Apply
    sudo sysctl -p
    ```

3. **Grant eBPF permissions** if you enabled eBPF. Ensure the SC4S container or process has the required capabilities.

4. **Restart SC4S** to apply the new configuration.

5. **Run performance tests** to validate your setup. See [Performance tests](performance-tests.md) for instructions.

## Testing the generated configuration

You can verify the generated configuration works by running SC4S and sending test events:

```bash
# Test with TCP
echo "Hello SC4S TCP test" | nc <sc4s_host> 514

# Test with UDP
echo "Hello SC4S UDP test" | nc -u <sc4s_host> 514
```

Confirm the events appear in Splunk by searching:

```
index=* "Hello SC4S"
```

## Further reading

- [Fine-tuning SC4S](fine-tuning.md) for detailed guidance on individual performance settings.
- [Performance tests](performance-tests.md) for benchmarking your deployment.
- [Configuration reference](../configuration.md) for the full list of SC4S environment variables.
- [Architecture overview](index.md) for protocol selection guidance.

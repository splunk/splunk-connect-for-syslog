# Finetune SC4S for UDP Traffic
This section demonstrates how SC4S can be vertically scaled by adjusting configuration parameters to significantly reduce UDP packet drops.

### Tested configuration:
- **Loggen** - c5.2xlarge
- **SC4S** (3.29.0) + podman - c5.4xlarge
- **Splunk Cloud** 9.2.2403.105 - 30IDX

| Setup for 67,000 EPS (Events per Second) | % Loss |
|------------------------------------------|--------|
| Default                                  | 77.88  |
| OS Kernel Tuning                         | 24.38  |
| Increasing the Number of UDP Sockets     | 22.95  |
| eBPF                                     | 0      |

Consider applying these changes to your infrastructure. After each adjustment, run the [performance tests](performance-tests.md#check-your-udp-performance) and retain the changes that result in improvements.

## Tune your receiving buffer

1. Update `/etc/sysctl.conf`

Change the default buffer size from:
```conf
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360
```

to 512MB:
```conf
net.core.rmem_default = 536870912
net.core.rmem_max = 536870912
```

And apply changes:
```bash
sudo sysctl -p
```

2. Update `/opt/sc4s/env_file`:
```bash
SC4S_SOURCE_UDP_SO_RCVBUFF=536870912
```

3. Restart SC4S:

## Tune UDP fetch limit
`/opt/sc4s/env_file`:
```bash
SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
```

## Increase the number of UDP sockets
`/opt/sc4s/env_file`:
```bash
SC4S_SOURCE_LISTEN_UDP_SOCKETS=32
```

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
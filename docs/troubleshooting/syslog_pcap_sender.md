# Syslog PCAP Sender

## Overview

`syslog_pcap_sender` is a universal Python script that extracts and replays syslog messages from PCAP files. It automatically 
detects whether the capture contains TCP or UDP traffic and uses the appropriate method to send messages to a syslog server.
Instead of replaying raw packets, `syslog_pcap_sender` extracts the syslog payloads and sends them over a fresh connection.

## Features

General:
- Automatically detects the used protocol from PCAP and in case of both uses the one with more entries
- Extracts only packets with syslog payloads
- Filters empty packets (TCP handshakes, UDP keepalives)
- Deduplicates TCP retransmissions (with option to disable it)

For TCP:
- Establishes fresh TCP connection with proper handshake
- Supports octet counting framing: `LENGTH MSG`
- Supports newline framing: `MSG\n`
- Avoids TCP sequence number issues from packet replay

For UDP:
- Sends UDP datagrams directly
- No connection state required

## Installation

### Requirements

- **Python:** 3.6 or higher
- **Scapy:** 2.4.0 or higher

### Install Dependencies

```bash
# Using pip
pip3 install scapy

# Or using apt (Debian/Ubuntu)
sudo apt-get install python3-scapy

# Or using yum (RHEL/CentOS)
sudo yum install python3-scapy
```

### Install Script

Download `syslog_pcap_sender` script from https://github.com/splunk/splunk-connect-for-syslog

```bash

# Make executable
chmod +x syslog_pcap_sender

# Verify installation
./syslog_pcap_sender --help
```

## Usage

Preview Messages (Safe - No Sending)
```bash
./syslog_pcap_sender -i capture.pcap --extract-only -v
```

Send to Syslog Server
```bash
./syslog_pcap_sender -i capture.pcap -H 192.168.1.100 -P 514 -s 192.168.1.99 
```

## Command-Line Options
| Option            | Short      | Description                                                                             | Protocol | Example           | Required         |
|-------------------|------------|-----------------------------------------------------------------------------------------|----------|-------------------|------------------|
| --input           | -i         | Input PCAP file to read                                                                 |          | -i capture.pcap   | Yes              |
| --dest-ip         | -d         | Destination syslog server IP address                                                    |          | -d 192.168.1.100  | Yes for sending  |
| --dest-port       | -p         | Destination port number                                                                 |          | -p 1514           | No (default 514) |
| --src-ip          | -s         | Source IP address for binding ( System will use default interface IP if not specified)  | UDP      | -s 192.168.1.10   | No               |
| --src-port        | -P         | Source port number ( System will assign random port if not specified)                   | UDP      | -P 5000           | No               |
| --newline-framing |            | Use newline framing instead of octet counting (RFC 6587)                                | TCP      | --newline-framing | No               |
| --delay           |            | Delay between sending messages (in seconds)                                             |          | --delay 0.1       | No               |
| --extract-only    |            | Extract and display payloads without sending                                            |          | --extract-only    | No               |
| --verbose         | -v         | Show sample messages during extraction Displays first 5 messages from capture           |          | -v                | No               |
| --force-tcp       |            | Force TCP mode even if UDP packets detected                                             |          | --force-tcp       | No               |
| --force-udp       |            | Force UDP mode even if TCP packets detected                                             |          | --force-udp       | No               |
| --no-deduplicate  | --no-dedup | Disable deduplication - send all payloads including duplicates. Not recommended for TCP |          | --no-dedup        | No               |
| --help            | -h         | Show help message and exit                                                              |          | -h                | No               |


## FAQ

### Q: Why use this instead of tcpreplay?

**A:** Traditional packet replay doesn't work for TCP syslog because:
- TCP requires valid connection state (sequence numbers)
- Replayed packets have old sequence numbers
- Destination rejects packets (no matching connection)

`syslog_pcap_sender` establishes a **fresh TCP connection** instead of replaying packets.

### Q: Does this work for both TCP and UDP?

**A:** Yes! It auto-detects and handles both.

### Q: Why there are fewer messages than packets?

**A:** PCAP contains:
- Empty packets (TCP handshakes, UDP keepalives)
- Duplicate packets (TCP retransmissions, capture artifacts)
- Other protocols (ARP, ICMP)

Only unique syslog payloads are sent.

### Q: Can I disable deduplication?

**A:** Yes, use `--no-dedup`, but not recommended for TCP (sends retransmissions as duplicates).

### Q: What if my PCAP has both TCP and UDP?

**A:** Use `--force-tcp` or `--force-udp` to specify, or process separately.
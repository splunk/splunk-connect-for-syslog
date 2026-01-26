#!/usr/bin/env python3
"""
Universal Syslog Sender - Automatically handles TCP or UDP syslog from PCAP

For TCP: Establishes fresh connection (avoids replay issues)
For UDP: Sends packets directly (replay-friendly)
"""

import sys
import socket
import argparse
import time
from scapy.all import rdpcap
from scapy.layers.inet import TCP, UDP
from scapy.packet import Raw


class SyslogSender:
    def __init__(self, pcap_file, dest_ip, dest_port=514, src_ip=None, src_port=None, no_dedup=False):
        self.pcap_file = pcap_file
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.src_ip = src_ip
        self.src_port = src_port
        self.no_dedup = no_dedup
        self.packets = []
        self.protocol = None
        self.payloads = []

    def analyze_pcap(self):
        """
        Read and analyze PCAP to determine protocol
        """
        print(f"Reading {self.pcap_file}...")
        try:
            self.packets = rdpcap(self.pcap_file)
        except Exception as e:
            print(f"Error reading PCAP: {e}", file=sys.stderr)
            sys.exit(1)

        if len(self.packets) == 0:
            print("No packets in PCAP file", file=sys.stderr)
            sys.exit(1)

        print(f"Loaded {len(self.packets)} packets")

        # Count protocols
        tcp_count = sum(1 for p in self.packets if TCP in p)
        udp_count = sum(1 for p in self.packets if UDP in p)

        print(f"\nProtocol Analysis:")
        print(f"  TCP packets: {tcp_count}")
        print(f"  UDP packets: {udp_count}")

        # Determine primary protocol
        if tcp_count > udp_count:
            self.protocol = 'TCP'
            print(f"\nDetected protocol: TCP")
        elif udp_count > 0:
            self.protocol = 'UDP'
            print(f"\nDetected protocol: UDP")
        else:
            print("No TCP or UDP packets found in PCAP", file=sys.stderr)
            sys.exit(1)

        return self.protocol

    def extract_payloads(self):
        """
        Extract syslog message payloads from packets
        """
        print(f"\nExtracting syslog payloads...")
        if self.no_dedup:
            print("  (Deduplication disabled - all payloads will be sent)")

        seen_payloads = set()  # Deduplicate retransmissions
        packets_with_payload = 0
        duplicate_count = 0

        for pkt in self.packets:
            payload = None

            # Extract payload based on protocol
            if self.protocol == 'TCP' and TCP in pkt and Raw in pkt:
                payload = bytes(pkt[Raw].load)
                packets_with_payload += 1
            elif self.protocol == 'UDP' and UDP in pkt and Raw in pkt:
                payload = bytes(pkt[Raw].load)
                packets_with_payload += 1

            if payload and len(payload) > 0:
                if self.no_dedup:
                    # No deduplication - add all payloads
                    self.payloads.append(payload)
                else:
                    # Deduplicate (important for TCP retransmissions)
                    payload_hash = hash(payload)
                    if payload_hash not in seen_payloads:
                        seen_payloads.add(payload_hash)
                        self.payloads.append(payload)
                    else:
                        duplicate_count += 1

        if self.no_dedup:
            print(f"Extracted {len(self.payloads)} syslog messages (including duplicates)")
        else:
            print(f"Extracted {len(self.payloads)} unique syslog messages")

        # Show filtering details
        protocol_packets = sum(1 for p in self.packets if (TCP in p if self.protocol == 'TCP' else UDP in p))
        packets_without_payload = protocol_packets - packets_with_payload

        if packets_without_payload > 0 or (duplicate_count > 0 and not self.no_dedup):
            print(f"  Filtering: {len(self.packets)} total packets → {len(self.payloads)} messages")
            if packets_without_payload > 0:
                print(f"    - {packets_without_payload} {self.protocol} packets without payload")
            if duplicate_count > 0 and not self.no_dedup:
                print(f"    - {duplicate_count} duplicate payloads (deduplicated)")

        if len(self.payloads) == 0:
            print("No syslog payloads found in packets", file=sys.stderr)
            sys.exit(1)

        return self.payloads

    def show_sample_messages(self, count=5):
        """
        Display sample messages from the capture
        """
        print(f"\nSample Messages (first {min(count, len(self.payloads))}):")

        for i, payload in enumerate(self.payloads[:count]):
            try:
                msg = payload.decode('utf-8', errors='ignore').strip()
                # Truncate long messages
                if len(msg) > 100:
                    msg = msg[:100] + "..."
                print(f"  [{i + 1}] {msg}")
            except:
                print(f"  [{i + 1}] <binary data, {len(payload)} bytes>")

        if len(self.payloads) > count:
            print(f"  ... and {len(self.payloads) - count} more messages")

    def send_tcp(self, octet_counting=True, delay=0):
        """
        Send syslog messages over TCP with fresh connection
        """
        print(f"\nConnecting to {self.dest_ip}:{self.dest_port} (TCP)...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            # Bind to specific source IP if specified
            if self.src_ip:
                try:
                    sock.bind((self.src_ip, 0))
                    print(f"Bound to source IP: {self.src_ip}")
                except Exception as e:
                    print(f"Warning: Could not bind to {self.src_ip}: {e}")

            sock.connect((self.dest_ip, self.dest_port))
            print("TCP connection established")

            sent_count = 0
            failed_count = 0

            for i, msg in enumerate(self.payloads):
                try:
                    # Decode message
                    if isinstance(msg, bytes):
                        msg_str = msg.decode('utf-8', errors='ignore')
                    else:
                        msg_str = str(msg)

                    # Remove existing newlines
                    msg_str = msg_str.rstrip('\n\r')

                    # Frame according to RFC 6587
                    if octet_counting:
                        # Octet counting: LENGTH SPACE MSG
                        msg_bytes = msg_str.encode('utf-8')
                        framed = f"{len(msg_bytes)} {msg_str}".encode('utf-8')
                    else:
                        # Non-transparent framing: MSG NEWLINE
                        framed = f"{msg_str}\n".encode('utf-8')

                    sock.sendall(framed)
                    sent_count += 1

                    # Progress indicator
                    if (i + 1) % 100 == 0 or (i + 1) == len(self.payloads):
                        print(f"Sent {i + 1}/{len(self.payloads)} messages...")

                    # Optional delay between messages
                    if delay > 0:
                        time.sleep(delay)

                except Exception as e:
                    print(f"Warning: Failed to send message {i + 1}: {e}", file=sys.stderr)
                    failed_count += 1

            print(f"\nTCP Send Complete:")
            print(f"Sent:   {sent_count}/{len(self.payloads)}")
            if failed_count > 0:
                print(f"Failed: {failed_count}")

            return sent_count > 0

        except socket.timeout:
            print(f"Connection timeout to {self.dest_ip}:{self.dest_port}", file=sys.stderr)
            return False
        except ConnectionRefusedError:
            print(f"Connection refused by {self.dest_ip}:{self.dest_port}", file=sys.stderr)
            print("Is the syslog server running and listening on TCP?", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        finally:
            sock.close()
            print("Connection closed")

    def send_udp(self, delay=0):
        """
        Send syslog messages over UDP
        """
        print(f"\n Sending to {self.dest_ip}:{self.dest_port} (UDP)...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind to specific source IP/port if specified
            if self.src_ip or self.src_port:
                bind_ip = self.src_ip or '0.0.0.0'
                bind_port = self.src_port or 0
                try:
                    sock.bind((bind_ip, bind_port))
                    print(f"Bound to {bind_ip}:{bind_port if bind_port else 'auto'}")
                except Exception as e:
                    print(f"Warning: Could not bind: {e}")

            sent_count = 0
            failed_count = 0

            for i, msg in enumerate(self.payloads):
                try:
                    # UDP syslog typically uses newline framing or just raw message
                    if isinstance(msg, bytes):
                        msg_bytes = msg
                    else:
                        msg_bytes = str(msg).encode('utf-8')

                    # Send datagram
                    sock.sendto(msg_bytes, (self.dest_ip, self.dest_port))
                    sent_count += 1

                    # Progress indicator
                    if (i + 1) % 100 == 0 or (i + 1) == len(self.payloads):
                        print(f"Sent {i + 1}/{len(self.payloads)} messages...")

                    # Optional delay between messages
                    if delay > 0:
                        time.sleep(delay)

                except Exception as e:
                    print(f"Warning: Failed to send message {i + 1}: {e}", file=sys.stderr)
                    failed_count += 1

            print(f"\nUDP Send Complete:")
            print(f"Sent:   {sent_count}/{len(self.payloads)}")
            if failed_count > 0:
                print(f"Failed: {failed_count}")

            return sent_count > 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        finally:
            sock.close()


def main():
    parser = argparse.ArgumentParser(
        description='Universal Syslog Sender - Auto-detects and sends TCP or UDP syslog from PCAP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect protocol and send
  %(prog)s -i capture.pcap -H 192.168.1.100 -P 514

  # Extract only (don't send)
  %(prog)s -i capture.pcap --extract-only -v

  # TCP with newline framing instead of octet counting
  %(prog)s -i tcp_capture.pcap -H 192.168.1.100 -P 514 --newline-framing

  # UDP with specific source IP
  %(prog)s -i udp_capture.pcap -H 192.168.1.100 -P 514 -s 192.168.1.10

  # Send with delay between messages (useful for rate limiting)
  %(prog)s -i capture.pcap -H 192.168.1.100 -P 514 --delay 0.1

Protocol Detection:
  The script automatically detects whether the PCAP contains TCP or UDP traffic
  and uses the appropriate sending method:

  TCP → Establishes fresh connection (avoids replay issues)
  UDP → Sends datagrams directly (simple replay)

For TCP Syslog:
  - Establishes new TCP connection with proper handshake
  - Avoids TCP sequence number issues from packet replay
  - Supports RFC 6587 framing (octet counting or newline)
  - Deduplicates retransmissions automatically

For UDP Syslog:
  - Sends UDP datagrams directly
  - No connection state issues
  - Works reliably for stateless protocols
        """
    )

    # Input/Output
    parser.add_argument('-i', '--input', required=True,
                        help='Input PCAP file')

    # Destination
    parser.add_argument('-H', '--host', '--dest-ip',
                        help='Destination syslog server IP')
    parser.add_argument('-P', '--port', '--dest-port', type=int, default=514,
                        help='Destination port (default: 514)')

    # Source (optional)
    parser.add_argument('-s', '--src-ip', '--source-ip',
                        help='Source IP address (optional, for binding)')
    parser.add_argument('-p', '--src-port', '--source-port', type=int,
                        help='Source port (optional, UDP only)')

    # TCP options
    parser.add_argument('--newline-framing', action='store_true',
                        help='TCP: Use newline framing instead of octet counting (RFC 6587)')

    # General options
    parser.add_argument('--delay', type=float, default=0,
                        help='Delay between messages in seconds (default: 0)')
    parser.add_argument('--extract-only', action='store_true',
                        help='Only extract and display payloads, don\'t send')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show extracted messages')
    parser.add_argument('--force-tcp', action='store_true',
                        help='Force TCP mode even if UDP packets detected')
    parser.add_argument('--force-udp', action='store_true',
                        help='Force UDP mode even if TCP packets detected')
    parser.add_argument('--no-dedup', '--no-deduplicate', action='store_true',
                        help='Disable deduplication - send all payloads including duplicates (not recommended for TCP)')

    args = parser.parse_args()

    # Initialize sender
    sender = SyslogSender(
        pcap_file=args.input,
        dest_ip=args.host,
        dest_port=args.port,
        src_ip=args.src_ip,
        src_port=args.src_port,
        no_dedup=args.no_dedup
    )

    # Analyze PCAP
    detected_protocol = sender.analyze_pcap()

    # Override protocol if forced
    if args.force_tcp:
        print(f"\nForcing TCP mode (detected: {detected_protocol})")
        sender.protocol = 'TCP'
    elif args.force_udp:
        print(f"\nForcing UDP mode (detected: {detected_protocol})")
        sender.protocol = 'UDP'

    # Extract payloads
    sender.extract_payloads()

    # Show samples if verbose or extract-only
    if args.verbose or args.extract_only:
        sender.show_sample_messages()

    # Exit if extract-only mode
    if args.extract_only:
        print(f"\nExtract-only mode: No messages sent")
        sys.exit(0)

    # Validate destination
    if not args.host:
        print("\nError: --host required for sending (or use --extract-only)",
              file=sys.stderr)
        print("Example: --host 192.168.1.100", file=sys.stderr)
        sys.exit(1)

    # Send messages based on protocol
    if sender.protocol == 'TCP':
        use_octet_counting = not args.newline_framing
        framing_type = "octet counting" if use_octet_counting else "newline framing"
        print(f"\nTCP framing: {framing_type}")

        success = sender.send_tcp(
            octet_counting=use_octet_counting,
            delay=args.delay
        )
    else:  # UDP
        success = sender.send_udp(delay=args.delay)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

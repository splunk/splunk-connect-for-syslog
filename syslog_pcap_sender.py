#!/usr/bin/env python3
"""
Universal Syslog Sender - Automatically handles TCP or UDP syslog from PCAP

For TCP: Reassembles TCP streams and parses syslog framing to extract complete messages
For UDP: Sends packets directly (replay-friendly)
"""

import sys
import socket
import argparse
import time
import re
from collections import defaultdict
from scapy.all import rdpcap
from scapy.layers.inet import TCP, UDP, IP
from scapy.packet import Raw


class SyslogSender:
    def __init__(self, pcap_file, dest_ip, dest_port=514, src_ip=None, src_port=None,
                 no_dedup=False, framing='auto'):
        self.pcap_file = pcap_file
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.src_ip = src_ip
        self.src_port = src_port
        self.no_dedup = no_dedup
        self.framing = framing
        self.packets = []
        self.protocol = None
        self.payloads = []
        self.detected_framing = None  # Store detected framing for TCP

    def analyze_pcap_packets(self):
        """
        Read and analyze PCAP to determine packets
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

    def set_protocol(self, force_tcp, force_udp):
        if force_tcp:
            print("\nForcing TCP mode")
            self.protocol = 'TCP'
        elif force_udp:
            print("\nForcing UDP mode")
            self.protocol = 'UDP'
        else:
            # Count protocols
            tcp_count = sum(1 for p in self.packets if TCP in p)
            udp_count = sum(1 for p in self.packets if UDP in p)

            print("\nProtocol Analysis:")
            print(f"  TCP packets: {tcp_count}")
            print(f"  UDP packets: {udp_count}")
            # Determine primary protocol
            if tcp_count > udp_count:
                self.protocol = 'TCP'
                print("\nDetected protocol: TCP")
            elif udp_count > 0:
                self.protocol = 'UDP'
                print("\nDetected protocol: UDP")
            else:
                print("No TCP or UDP packets found in PCAP", file=sys.stderr)
                sys.exit(1)

    @staticmethod
    def _is_segment_seen(seq, seg_end, seen_ranges):
        """
        Return True if [seq, seg_end) is fully contained in already-seen data
        (i.e. a retransmission).
        """
        for seen_start, seen_end in seen_ranges:
            if seq >= seen_start and seg_end <= seen_end:
                return True
        return False

    def _dedupe_stream_segments(self, segments):
        """
        Concatenate sorted segments, skipping retransmissions that are fully
        contained in already-seen data. Returns the reassembled bytes.
        """
        result = bytearray()
        seen_ranges = []

        for seq, payload in segments:
            # Check if this segment overlaps with already processed data
            seg_end = seq + len(payload)
            if self._is_segment_seen(seq, seg_end, seen_ranges):
                continue
            result.extend(payload)
            seen_ranges.append((seq, seg_end))

        return bytes(result)

    def _sort_tcp_streams_by_sequence(self, streams):
        """
        Sort each stream by sequence number and concatenate
        """
        reassembled = {}
        for stream_key, segments in streams.items():
            # Sort by sequence number
            segments.sort(key=lambda x: x[0])

            # Deduplicate overlapping segments (retransmissions)
            result = self._dedupe_stream_segments(segments)

            if len(result) > 0:
                reassembled[stream_key] = result

        return reassembled

    def _reassemble_tcp_streams(self):
        """
        Reassemble TCP streams by grouping packets by connection and ordering by sequence number.
        Returns a dict of {connection_tuple: reassembled_bytes}
        """
        streams = defaultdict(list)

        for pkt in self.packets:
            if TCP in pkt and IP in pkt and Raw in pkt:
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                src_port = pkt[TCP].sport
                dst_port = pkt[TCP].dport
                seq = pkt[TCP].seq
                payload = bytes(pkt[Raw].load)

                if len(payload) > 0:
                    # Use unidirectional stream key (we want to follow one direction)
                    stream_key = (src_ip, src_port, dst_ip, dst_port)
                    streams[stream_key].append((seq, payload))

        reassembled = self._sort_tcp_streams_by_sequence(streams)
        return reassembled

    def _detect_framing_type(self, data):
        """
        Auto-detect the framing type used in the stream.
        Returns 'octet-counting' or 'newline'
        """
        # Try to detect octet-counting: starts with digits followed by space
        # Example: "123 <14>..." or "45 <134>..."
        if re.match(rb'^\d+ <\d+>', data[:50]):
            return 'octet-counting'

        # Check if we have newline-separated messages that look like syslog
        lines = data.split(b'\n')
        syslog_pattern = rb'<\d+>'
        syslog_lines = sum(1 for line in lines[:10] if re.search(syslog_pattern, line))

        if syslog_lines > 0:
            return 'newline'

        # Default to newline if unclear
        return 'newline'

    @staticmethod
    def _skip_octet_whitespace(data, pos):
        """
        Advance past leading whitespace and return the new position.
        """
        data_len = len(data)
        while pos < data_len and data[pos:pos + 1] in (b' ', b'\n', b'\r', b'\t'):
            pos += 1
        return pos

    @staticmethod
    def _read_octet_length(data, pos):
        """
        Read the leading length field (digits) starting at pos.
        Returns (msg_length, new_pos), or (None, pos) if no valid length is found.
        """
        data_len = len(data)
        length_start = pos
        while pos < data_len and data[pos:pos + 1].isdigit():
            pos += 1

        if pos == length_start:
            # No length found, might be corrupted or end of stream
            return None, pos

        try:
            msg_length = int(data[length_start:pos])
        except ValueError:
            return None, pos

        # Skip the space after length
        if pos < data_len and data[pos:pos + 1] == b' ':
            pos += 1

        return msg_length, pos

    def _parse_octet_counting(self, data):
        """
        Parse syslog messages using octet-counting framing (RFC 6587).
        Format: LENGTH SP MSG LENGTH SP MSG ...
        """
        messages = []
        pos = 0
        data_len = len(data)

        while pos < data_len:
            pos = self._skip_octet_whitespace(data, pos)
            if pos >= data_len:
                break

            # Read the length (digits until space)
            msg_length, pos = self._read_octet_length(data, pos)
            if msg_length is None:
                break

            # Read the message
            if pos + msg_length <= data_len:
                msg = data[pos:pos + msg_length]
                messages.append(msg)
                pos += msg_length
            else:
                # Incomplete message at end of stream
                # Take what we have
                remaining = data[pos:]
                if len(remaining) > 0:
                    messages.append(remaining)
                break

        return messages

    def _parse_newline_framing(self, data):
        """
        Parse syslog messages using newline framing.
        """
        messages = []
        lines = data.split(b'\n')

        for line in lines:
            line = line.strip()
            if len(line) > 0:
                messages.append(line)

        return messages

    def _parse_syslog_messages(self, data, framing_type):
        """
        Parse syslog messages from reassembled stream based on framing type.
        """
        if framing_type == 'octet-counting':
            return self._parse_octet_counting(data)
        else:
            return self._parse_newline_framing(data)

    def extract_payloads(self):
        """
        Extract syslog message payloads from packets.
        For TCP: Reassembles streams and parses framing.
        For UDP: Extracts per-packet payloads.
        """
        print("\nExtracting syslog payloads...")

        if self.protocol == 'TCP':
            return self._extract_tcp_payloads()
        else:
            return self._extract_udp_payloads()

    def _process_tcp_payload(self, stream_data, seen_payloads, duplicate_count):
            # Determine framing type
            if self.framing == 'auto':
                framing_type = self._detect_framing_type(stream_data)
            else:
                framing_type = self.framing

            # Store the framing type for sending
            self.detected_framing = framing_type

            # Parse messages from stream
            messages = self._parse_syslog_messages(stream_data, framing_type)

            for msg in messages:
                if self.no_dedup:
                    self.payloads.append(msg)
                else:
                    if msg not in seen_payloads:
                        seen_payloads.add(msg)
                        self.payloads.append(msg)
                    else:
                        duplicate_count += 1
            
            return seen_payloads, duplicate_count

    def _extract_tcp_payloads(self):
        """
        Extract payloads from TCP by reassembling streams and parsing framing.
        """
        print("  Reassembling TCP streams...")

        # Reassemble TCP streams
        streams = self._reassemble_tcp_streams()

        if len(streams) == 0:
            print("No TCP streams with payload found", file=sys.stderr)
            sys.exit(1)

        print(f"  Found {len(streams)} TCP stream(s)")

        # Process each stream
        seen_payloads = set()
        duplicate_count = 0

        for _, stream_data in streams.items():
            seen_payloads, duplicate_count = self._process_tcp_payload(stream_data, seen_payloads, duplicate_count)

        if self.no_dedup:
            print(f"\nExtracted {len(self.payloads)} syslog messages (including duplicates)")
        else:
            print(f"\nExtracted {len(self.payloads)} unique syslog messages")
            if duplicate_count > 0:
                print(f"  ({duplicate_count} duplicates removed)")

        if len(self.payloads) == 0:
            print("No syslog payloads found in TCP streams", file=sys.stderr)
            sys.exit(1)

        return self.payloads

    def _process_udp_pkt(self, pkt, seen_payloads, packets_with_payload, duplicate_count):
        payload = bytes(pkt[Raw].load)
        packets_with_payload += 1

        if payload and len(payload) > 0:
            if self.no_dedup:
                self.payloads.append(payload)
            else:
                if payload not in seen_payloads:
                    seen_payloads.add(payload)
                    self.payloads.append(payload)
                else:
                    duplicate_count += 1

        return seen_payloads, packets_with_payload, duplicate_count


    def _collect_udp_payloads(self):
        """
        Iterate UDP packets and collect payloads.
        Returns (packets_with_payload, duplicate_count).
        """
        seen_payloads = set()
        packets_with_payload = 0
        duplicate_count = 0

        for pkt in self.packets:
            if not (UDP in pkt and Raw in pkt):
                continue

            seen_payloads, packets_with_payload, duplicate_count = self._process_udp_pkt(
                pkt, seen_payloads, packets_with_payload, duplicate_count)

        return packets_with_payload, duplicate_count

    def _print_udp_filtering_details(self, packets_with_payload, duplicate_count):
        """
        Print the UDP extraction summary and filtering breakdown.
        """
        if self.no_dedup:
            print(f"Extracted {len(self.payloads)} syslog messages (including duplicates)")
        else:
            print(f"Extracted {len(self.payloads)} unique syslog messages")

        # Show filtering details
        udp_packets = sum(1 for p in self.packets if UDP in p)
        packets_without_payload = udp_packets - packets_with_payload

        if packets_without_payload > 0 or (duplicate_count > 0 and not self.no_dedup):
            print(f"  Filtering: {len(self.packets)} total packets → {len(self.payloads)} messages")
            if packets_without_payload > 0:
                print(f"    - {packets_without_payload} UDP packets without payload")
            if duplicate_count > 0 and not self.no_dedup:
                print(f"    - {duplicate_count} duplicate payloads (deduplicated)")

    def _extract_udp_payloads(self):
        """
        Extract payloads from UDP packets (one message per packet).
        """
        if self.no_dedup:
            print("  (Deduplication disabled - all payloads will be sent)")

        packets_with_payload, duplicate_count = self._collect_udp_payloads()

        self._print_udp_filtering_details(packets_with_payload, duplicate_count)

        if len(self.payloads) == 0:
            print("No syslog payloads found in packets", file=sys.stderr)
            sys.exit(1)

        return self.payloads

    def show_sample_messages(self, count=5):
        """
        Display sample messages from the capture
        """
        print(f"\nSample Messages (first {min(count, len(self.payloads))}):")

        for i, payload in enumerate(self.payloads[:count], 1):
            try:
                msg = payload.decode('utf-8', errors='ignore').strip()
                # Truncate long messages
                if len(msg) > 100:
                    msg = msg[:100] + "..."
                print(f"  [{i}] {msg}")
            except Exception:
                print(f"  [{i}] <binary data, {len(payload)} bytes>")

        if len(self.payloads) > count:
            print(f"  ... and {len(self.payloads) - count} more messages")

    def _frame_tcp_message(self, msg):
        """
        Frame a single message for TCP per RFC 6587, using the detected framing.
        """
        # Decode message
        if isinstance(msg, bytes):
            msg_str = msg.decode('utf-8', errors='ignore')
        else:
            msg_str = str(msg)

        # Remove existing framing (newlines, length prefixes)
        msg_str = msg_str.strip()

        # Frame according to RFC 6587 using the same framing as input
        if self.detected_framing == 'octet-counting':
            # Octet counting: LENGTH SPACE MSG
            msg_bytes = msg_str.encode('utf-8')
            return f"{len(msg_bytes)} ".encode('utf-8') + msg_bytes
        # Non-transparent framing: MSG NEWLINE
        return f"{msg_str}\n".encode('utf-8')

    def _frame_udp_message(self, msg):
        """
        Frame a single message for UDP (raw bytes / newline framing).
        """
        # UDP syslog typically uses newline framing or just raw message
        if isinstance(msg, bytes):
            return msg
        return str(msg).encode('utf-8')

    def _report_send_progress(self, index):
        """
        Print a progress line every 100 messages and on the final message.
        """
        if (index + 1) % 100 == 0 or (index + 1) == len(self.payloads):
            print(f"Sent {index + 1}/{len(self.payloads)} messages...")

    def _send_payloads(self, send_func, delay):
        """
        Send all payloads via send_func, handling progress, delay and per-message
        errors. Returns (sent_count, failed_count).
        """
        sent_count = 0
        failed_count = 0

        for i, msg in enumerate(self.payloads):
            try:
                send_func(msg)
                sent_count += 1

                # Progress indicator
                self._report_send_progress(i)

                # Optional delay between messages
                if delay > 0:
                    time.sleep(delay)

            except Exception as e:
                print(f"Warning: Failed to send message {i + 1}: {e}", file=sys.stderr)
                failed_count += 1

        return sent_count, failed_count

    def _print_send_summary(self, label, sent_count, failed_count):
        """
        Print the post-send summary block shared by TCP and UDP.
        """
        print(f"\n{label} Send Complete:")
        print(f"Sent:   {sent_count}/{len(self.payloads)}")
        if failed_count > 0:
            print(f"Failed: {failed_count}")

    def _bind_tcp_source(self, sock):
        """
        Bind the TCP socket to the configured source IP, if any.
        """
        if self.src_ip:
            try:
                sock.bind((self.src_ip, 0))
                print(f"Bound to source IP: {self.src_ip}")
            except Exception as e:
                print(f"Warning: Could not bind to {self.src_ip}: {e}")

    def send_tcp(self, delay=0):
        """
        Send syslog messages over TCP with fresh connection using detected framing
        """
        print(f"\nConnecting to {self.dest_ip}:{self.dest_port} (TCP)...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            # Bind to specific source IP if specified
            self._bind_tcp_source(sock)

            sock.connect((self.dest_ip, self.dest_port))
            print("TCP connection established")

            sent_count, failed_count = self._send_payloads(
                lambda msg: sock.sendall(self._frame_tcp_message(msg)), delay)

            self._print_send_summary("TCP", sent_count, failed_count)

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

    def _bind_udp_source(self, sock):
        """
        Bind the UDP socket to the configured source IP/port, if any.
        """
        if self.src_ip or self.src_port:
            bind_ip = self.src_ip or '0.0.0.0'
            bind_port = self.src_port or 0
            try:
                sock.bind((bind_ip, bind_port))
                print(f"Bound to {bind_ip}:{bind_port if bind_port else 'auto'}")
            except Exception as e:
                print(f"Warning: Could not bind: {e}")

    def send_udp(self, delay=0):
        """
        Send syslog messages over UDP
        """
        print(f"\nSending to {self.dest_ip}:{self.dest_port} (UDP)...")

        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Bind to specific source IP/port if specified
            self._bind_udp_source(sock)

            sent_count, failed_count = self._send_payloads(
                lambda msg: sock.sendto(self._frame_udp_message(msg), (self.dest_ip, self.dest_port)),
                delay)

            self._print_send_summary("UDP", sent_count, failed_count)

            return sent_count > 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
        finally:
            if sock:
                sock.close()


def main():
    parser = argparse.ArgumentParser(
        description='Universal Syslog Sender - Auto-detects and sends TCP or UDP syslog from PCAP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect protocol and send
  %(prog)s -i capture.pcap -d 192.168.1.100 -p 514

  # Extract only (don't send)
  %(prog)s -i capture.pcap --extract-only -v

  # Specify framing type (applies to both parsing and sending)
  %(prog)s -i capture.pcap -d 192.168.1.100 --framing newline
  %(prog)s -i capture.pcap -d 192.168.1.100 --framing octet-counting

  # UDP with specific source IP
  %(prog)s -i udp_capture.pcap -d 192.168.1.100 -p 514 -s 192.168.1.10

  # Send with delay between messages (useful for rate limiting)
  %(prog)s -i capture.pcap -d 192.168.1.100 -p 514 --delay 0.1
   """
    )

    # Input/Output
    parser.add_argument('-i', '--input', required=True,
                        help='Input PCAP file')

    # Destination
    parser.add_argument('-d', '--dest-ip',
                        help='Destination syslog server IP')
    parser.add_argument('-p', '--dest-port', type=int, default=514,
                        help='Destination port (default: 514)')

    # Source (optional)
    parser.add_argument('-s', '--src-ip',
                        help='Source IP address (optional, for binding)')
    parser.add_argument('-P', '--src-port', type=int,
                        help='Source port (optional, UDP only)')

    # TCP framing options
    parser.add_argument('-f', '--framing', choices=['auto', 'octet-counting', 'newline'],
                        default='auto', dest='framing',
                        help='TCP framing type for parsing PCAP and sending (default: auto-detect)')

    # TCP connection options
    parser.add_argument('--batch-size', type=int, default=None,
                        help='TCP: Send N messages per connection, then reconnect (default: all messages in one connection)')
    parser.add_argument('--no-reconnect', action='store_true',
                        help='TCP: Stop on first connection error instead of reconnecting')

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
                        help='Disable deduplication - send all payloads including duplicates')

    args = parser.parse_args()

    # Initialize sender
    sender = SyslogSender(
        pcap_file=args.input,
        dest_ip=args.dest_ip,
        dest_port=args.dest_port,
        src_ip=args.src_ip,
        src_port=args.src_port,
        no_dedup=args.no_dedup,
        framing=args.framing
    )

    # Analyze PCAP packets and protocol set
    sender.analyze_pcap_packets()
    sender.set_protocol(args.force_tcp, args.force_udp)


    # Extract payloads
    sender.extract_payloads()

    # Show samples if verbose or extract-only
    if args.verbose or args.extract_only:
        sender.show_sample_messages()

    # Exit if extract-only mode
    if args.extract_only:
        print("\nExtract-only mode: No messages sent")
        sys.exit(0)

    # Validate destination
    if not args.dest_ip:
        print("\nError: --dest-ip required for sending (or use --extract-only)",
              file=sys.stderr)
        print("Example: --dest-ip 192.168.1.100", file=sys.stderr)
        sys.exit(1)

    # Send messages based on protocol
    if sender.protocol == 'TCP':
        framing_type = "octet counting" if sender.detected_framing == 'octet-counting' else "newline"
        print(f"\nTCP framing (parsing & sending): {framing_type}")

        success = sender.send_tcp(delay=args.delay)
    else:  # UDP
        success = sender.send_udp(delay=args.delay)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

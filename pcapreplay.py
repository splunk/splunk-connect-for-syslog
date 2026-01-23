#!/usr/bin/env python3
"""
Convert Linux Cooked Capture to Ethernet frames for replay
"""

import sys
import argparse
from scapy.all import *


def convert_cooked_to_ethernet(pkt, src_mac, dst_mac):
    """
    Convert Linux cooked capture packet to Ethernet frame
    """
    # Check if it's a cooked packet
    if pkt.name == "cooked linux":
        # Extract the payload (IP layer and above)
        if IP in pkt:
            payload = pkt[IP]

            # Create new Ethernet frame with the payload
            eth_pkt = Ether(src=src_mac, dst=dst_mac) / payload
            return eth_pkt
        else:
            print(f"Warning: Cooked packet has no IP layer", file=sys.stderr)
            return None
    elif Ether in pkt:
        # Already has Ethernet, just return it
        return pkt
    else:
        print(f"Warning: Unknown packet type: {pkt.name}", file=sys.stderr)
        return None


def rewrite_and_convert(input_file, output_file, **kwargs):
    """
    Convert cooked capture to Ethernet and rewrite addresses
    """

    print(f"Reading packets from {input_file}...")
    try:
        packets = rdpcap(input_file)
    except Exception as e:
        print(f"Error reading PCAP file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Total packets: {len(packets)}")

    # Check packet type
    if len(packets) > 0:
        first_pkt = packets[0]
        print(f"\nFirst packet type: {first_pkt.name}")

        if first_pkt.name == "cooked linux":
            print("  ℹ This is a Linux Cooked Capture - will convert to Ethernet")
        elif Ether in first_pkt:
            print("  ✓ Already has Ethernet layer")
        print()

    # Check required parameters for cooked capture
    if packets[0].name == "cooked linux":
        if not kwargs.get('src_mac') or not kwargs.get('dst_mac'):
            print("Error: Linux Cooked Capture requires -M (src MAC) and -m (dst MAC)", file=sys.stderr)
            sys.exit(1)

    converted_packets = []
    stats = {
        'total': len(packets),
        'converted': 0,
        'modified': 0,
        'errors': 0
    }

    print("Processing packets...")
    for i, pkt in enumerate(packets):
        try:
            # Step 1: Convert cooked to Ethernet if needed
            if pkt.name == "cooked linux":
                new_pkt = convert_cooked_to_ethernet(
                    pkt,
                    kwargs.get('src_mac', '00:00:00:00:00:00'),
                    kwargs.get('dst_mac', '00:00:00:00:00:00')
                )
                if new_pkt is None:
                    stats['errors'] += 1
                    continue
                stats['converted'] += 1
            else:
                new_pkt = pkt.copy()

            # Step 2: Modify IP addresses if specified
            if IP in new_pkt:
                if kwargs.get('src_ip'):
                    new_pkt[IP].src = kwargs['src_ip']
                    stats['modified'] += 1

                if kwargs.get('dst_ip'):
                    new_pkt[IP].dst = kwargs['dst_ip']
                    stats['modified'] += 1

                # Delete checksums to force recalc
                del new_pkt[IP].chksum
                del new_pkt[IP].len

            # Step 3: Modify ports if specified
            if UDP in new_pkt:
                if kwargs.get('src_port'):
                    new_pkt[UDP].sport = int(kwargs['src_port'])
                    stats['modified'] += 1

                if kwargs.get('dst_port'):
                    new_pkt[UDP].dport = int(kwargs['dst_port'])
                    stats['modified'] += 1

                del new_pkt[UDP].chksum
                del new_pkt[UDP].len

            if TCP in new_pkt:
                if kwargs.get('src_port'):
                    new_pkt[TCP].sport = int(kwargs['src_port'])
                    stats['modified'] += 1

                if kwargs.get('dst_port'):
                    new_pkt[TCP].dport = int(kwargs['dst_port'])
                    stats['modified'] += 1

                del new_pkt[TCP].chksum

            # Step 4: Rebuild packet to recalculate checksums
            new_pkt = new_pkt.__class__(bytes(new_pkt))

            converted_packets.append(new_pkt)

            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(packets)} packets...")

        except Exception as e:
            print(f"Warning: Error processing packet {i}: {e}", file=sys.stderr)
            stats['errors'] += 1

    print(f"\nConversion Statistics:")
    print(f"  Total packets:           {stats['total']}")
    print(f"  Cooked -> Ethernet:      {stats['converted']}")
    print(f"  Successfully processed:  {len(converted_packets)}")
    print(f"  Errors:                  {stats['errors']}")

    if len(converted_packets) == 0:
        print("\nError: No packets to write!", file=sys.stderr)
        sys.exit(1)

    print(f"\nWriting converted packets to {output_file}...")
    try:
        wrpcap(output_file, converted_packets)
        print(f"✓ Successfully wrote {len(converted_packets)} packets")
    except Exception as e:
        print(f"Error writing PCAP file: {e}", file=sys.stderr)
        sys.exit(1)

    # Verify first packet
    print("\nVerifying first converted packet:")
    first = converted_packets[0]
    if Ether in first:
        print(f"  ✓ Ethernet layer present")
        print(f"    Src MAC: {first[Ether].src}")
        print(f"    Dst MAC: {first[Ether].dst}")
    if IP in first:
        print(f"  ✓ IP layer present")
        print(f"    Src IP:  {first[IP].src}")
        print(f"    Dst IP:  {first[IP].dst}")
    if UDP in first:
        print(f"  ✓ UDP layer present")
        print(f"    Src Port: {first[UDP].sport}")
        print(f"    Dst Port: {first[UDP].dport}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Convert Linux Cooked Capture to Ethernet and rewrite addresses',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert cooked capture to Ethernet for replay
  %(prog)s -i cooked.pcap -o ethernet.pcap \\
      -M 0a:ff:e9:44:0b:75 -m 0a:06:2f:b0:df:13 \\
      -s 172.31.20.139 -d 54.145.13.9 -P 514
        """
    )

    parser.add_argument('-i', '--input', required=True, help='Input PCAP file')
    parser.add_argument('-o', '--output', required=True, help='Output PCAP file')
    parser.add_argument('-s', '--src-ip', help='Source IP address')
    parser.add_argument('-d', '--dst-ip', help='Destination IP address')
    parser.add_argument('-p', '--src-port', help='Source port')
    parser.add_argument('-P', '--dst-port', help='Destination port')
    parser.add_argument('-M', '--src-mac', required=True, help='Source MAC address (YOUR interface)')
    parser.add_argument('-m', '--dst-mac', required=True, help='Destination MAC address (YOUR gateway)')

    args = parser.parse_args()

    # Build rewrite parameters
    rewrite_params = {
        'src_mac': args.src_mac,
        'dst_mac': args.dst_mac
    }

    if args.src_ip:
        rewrite_params['src_ip'] = args.src_ip

    if args.dst_ip:
        rewrite_params['dst_ip'] = args.dst_ip

    if args.src_port:
        rewrite_params['src_port'] = args.src_port

    if args.dst_port:
        rewrite_params['dst_port'] = args.dst_port

    # Perform conversion and rewrite
    rewrite_and_convert(args.input, args.output, **rewrite_params)


if __name__ == '__main__':
    main()
#!/bin/bash

# Description: Rewrites checksums in a PCAP file and replays it on a network interface

# Check if required tools are installed
command -v tcprewrite >/dev/null 2>&1 || { echo "Error: tcprewrite is not installed. Install tcpreplay package." >&2; exit 1; }
command -v tcpreplay >/dev/null 2>&1 || { echo "Error: tcpreplay is not installed. Install tcpreplay package." >&2; exit 1; }

# Check arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <input.pcap> <interface> [options]"
    echo ""
    echo "Options:"
    echo "  -s <speed>     Replay speed multiplier (e.g., 2 for 2x speed)"
    echo "  -l <loop>      Number of times to loop the pcap (default: 1)"
    echo ""
    echo "Example: $0 capture.pcap eth0"
    echo "Example: $0 capture.pcap eth0 -s 2 -l 3"
    exit 1
fi

# Input parameters
INPUT_PCAP="$1"
INTERFACE="$2"
OUTPUT_PCAP="${INPUT_PCAP%.pcap}_rewritten.pcap"

# Optional parameters
SPEED=""
LOOP=""

shift 2
while [ "$#" -gt 0 ]; do
    case "$1" in
        -s)
            SPEED="--multiplier=$2"
            shift 2
            ;;
        -l)
            LOOP="--loop=$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate input file
if [ ! -f "$INPUT_PCAP" ]; then
    echo "Error: Input file '$INPUT_PCAP' not found!"
    exit 1
fi

# Validate interface
if ! ip link show "$INTERFACE" >/dev/null 2>&1; then
    echo "Error: Interface '$INTERFACE' does not exist!"
    echo "Available interfaces:"
    ip -brief link show
    exit 1
fi

# Step 1: Rewrite checksums
echo "[*] Rewriting checksums for $INPUT_PCAP..."
tcprewrite --fixcsum --infile="$INPUT_PCAP" --outfile="$OUTPUT_PCAP"

if [ $? -ne 0 ]; then
    echo "Error: Failed to rewrite checksums!"
    exit 1
fi

echo "[+] Checksums rewritten successfully: $OUTPUT_PCAP"

# Step 2: Replay the modified pcap
echo "[*] Replaying $OUTPUT_PCAP on interface $INTERFACE..."
sudo tcpreplay --intf1="$INTERFACE" $SPEED $LOOP "$OUTPUT_PCAP"

if [ $? -eq 0 ]; then
    echo "[+] Replay completed successfully!"
    # Clean up rewritten file
    rm -f "$OUTPUT_PCAP"
    echo "[+] Rewritten file cleaned up."
else
    echo "Error: Replay failed!"
    # Clean up even on failure
    rm -f "$OUTPUT_PCAP"
    exit 1
fi
#!/bin/bash
# filepath: configuration-tool.sh

# SC4S Configuration Tool
# Generates a customized env_file based on user requirements

set -e

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Initialize variables
OUTPUT_FILE="env_file"
SPLUNK_URL=""
HEC_TOKEN=""
TLS_VERIFY="yes"
EXPECTED_EPS=1000
PROTOCOL="both"

ADJUST_FETCH_LIMIT="no"
ADJUST_LISTEN_SOCKETS="no"
SC4S_SOURCE_LISTEN_UDP_SOCKETS=2
SC4S_SOURCE_UDP_FETCH_LIMIT=1000
SC4S_ENABLE_EBPF="no"
SC4S_EBPF_NO_SOCKETS=4

PARALLELIZE="no"
SC4S_PARALLELIZE_NO_PARTITION=4
SC4S_SOURCE_TCP_IW_USE="no"
SC4S_SOURCE_TCP_IW_SIZE=1000000

SC4S_SOURCE_UDP_SO_RCVBUFF=-1
SC4S_SOURCE_TCP_SO_RCVBUFF=-1

SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE="yes"
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE="no"
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=10241024
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH=15000
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=53687091200

echo ""
printf "${BLUE}================================================${NC}\n"
printf "${BLUE}    SC4S Configuration Tool${NC}\n"
printf "${BLUE}================================================${NC}\n"
echo ""
echo "This tool will help you generate an optimized SC4S configuration"
echo "based on your requirements."
echo ""

# Validate HEC URL: must start with http:// or https://, have a hostname, and optionally a port
validate_hec_url() {
    local url="$1"
    if [[ "$url" =~ ^https?://[a-zA-Z0-9._-]+(:[0-9]+)?(/.*)?$ ]]; then
        return 0
    fi
    return 1
}

# Validate HEC token: must be a non-empty UUID-like string (8-4-4-4-12 hex)
validate_hec_token() {
    local token="$1"
    if [[ "$token" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ]]; then
        return 0
    fi
    return 1
}

# Prompt for HEC URL with validation, retries until valid
read_hec_url() {
    local input
    while true; do
        read -p "Enter your Splunk HEC URL (e.g., https://your.splunk.instance:8088): " input
        if [ -z "$input" ]; then
            printf "${RED}HEC URL cannot be empty.${NC}\n"
        elif validate_hec_url "$input"; then
            SPLUNK_URL="$input"
            break
        else
            printf "${RED}Invalid URL format. Must start with http:// or https:// followed by a hostname.${NC}\n"
            printf "${YELLOW}Example: https://splunk.example.com:8088${NC}\n"
        fi
    done
}

# Prompt for HEC token with validation, retries until valid; input is masked
read_hec_token() {
    local input
    while true; do
        read -p "Enter your Splunk HEC Token: " input
        if [ -z "$input" ]; then
            printf "${RED}HEC Token cannot be empty.${NC}\n"
        elif validate_hec_token "$input"; then
            HEC_TOKEN="$input"
            break
        else
            printf "${RED}Invalid token format. Expected a UUID (e.g., 12345678-1234-1234-1234-123456789abc).${NC}\n"
        fi
    done
}

# Function to ask yes/no questions
ask_yes_no() {
    local question="$1"
    local default="$2"
    local response
    
    while true; do
        if [ "$default" = "yes" ]; then
            read -p "$question [Y/n]: " response
            response=${response:-y}
        else
            read -p "$question [y/N]: " response
            response=${response:-n}
        fi
        
        case "$response" in
            [Yy]*|yes*|Yes*|YES* ) echo "yes"; break;;
            [Nn]*|no*|No*|NO* ) echo "no"; break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Function to apply hardware-based configuration
apply_hardware_config() {
    local hardware="$1"
    local protocol="$2"
    local expected_eps="$3"
    
    echo ""
    printf "${BLUE}Applying configuration for $hardware with $protocol protocol${NC}\n"
    printf "${BLUE}Expected EPS: $expected_eps${NC}\n"
    
    case "$hardware" in
        "16vCPUs")
            # 16 vCPUs, 64 GB RAM
            
            if [ "$protocol" = "udp" ]; then
                if [ "$expected_eps" -gt 35000 ]; then
                    ADJUST_FETCH_LIMIT="yes"
                    SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                    SC4S_ENABLE_EBPF="yes"
                    SC4S_EBPF_NO_SOCKETS=16
                    SC4S_SOURCE_UDP_SO_RCVBUFF=536870912
                fi
            elif [ "$protocol" = "tcp" ]; then
                if [ "$expected_eps" -gt 50000 ]; then
                    PARALLELIZE="yes"
                    SC4S_PARALLELIZE_NO_PARTITION=8
                    SC4S_SOURCE_TCP_SO_RCVBUFF=536870912
                fi
            fi
            ;;
            
        "8vCPUs")
            # 8 vCPUs, 32 GB RAM
            
            if [ "$protocol" = "udp" ]; then
                if [ "$expected_eps" -gt 25000 ]; then
                    ADJUST_FETCH_LIMIT="yes"
                    SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                    SC4S_ENABLE_EBPF="yes"
                    SC4S_EBPF_NO_SOCKETS=16
                    SC4S_SOURCE_UDP_SO_RCVBUFF=268435456
                fi
            elif [ "$protocol" = "tcp" ]; then
                if [ "$expected_eps" -gt 30000 ]; then
                    PARALLELIZE="yes"
                    SC4S_PARALLELIZE_NO_PARTITION=8
                    SC4S_SOURCE_TCP_SO_RCVBUFF=268435456
                fi
            fi
            ;;
            
        "4vCPUs")
            # 4 vCPUs, 16 GB RAM
            
            if [ "$protocol" = "udp" ]; then
                if [ "$expected_eps" -gt 10000 ]; then
                    ADJUST_FETCH_LIMIT="yes"
                    SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                    SC4S_ENABLE_EBPF="yes"
                    SC4S_EBPF_NO_SOCKETS=8
                    SC4S_SOURCE_UDP_SO_RCVBUFF=268435456
                fi
            elif [ "$protocol" = "tcp" ]; then
                if [ "$expected_eps" -gt 20000 ]; then
                    PARALLELIZE="yes"
                    SC4S_PARALLELIZE_NO_PARTITION=4
                    SC4S_SOURCE_TCP_SO_RCVBUFF=268435456
                fi
            fi
            ;;
    esac
}

# Mode selection
printf "${GREEN}=== Configuration Mode ===${NC}\n"
echo ""
echo "Choose configuration mode:"
echo "1) Custom configuration (default)"
echo "2) Hardware-based configuration (estimate based on hardware and events per second)"
echo ""
read -p "Select mode [1]: " mode_choice
mode_choice=${mode_choice:-1}

if [ "$mode_choice" = "2" ]; then
    # Hardware-based mode
    echo ""
    printf "${GREEN}=== Hardware-Based Configuration ===${NC}\n"
    echo ""
    echo "Select type of instance most similar to your hardware:"
    echo "1) 16 vCPUs, 64 GB RAM (like m5.4xlarge EC2)"
    echo "2) 8 vCPUs, 32 GB RAM (like m5.2xlarge EC2)"
    echo "3) 4 vCPUs, 16 GB RAM (like m5.xlarge EC2)"
    echo ""
    read -p "Select hardware [2]: " hw_choice
    hw_choice=${hw_choice:-2}
    
    case "$hw_choice" in
        1) HARDWARE="16vCPUs";;
        2) HARDWARE="8vCPUs";;
        3) HARDWARE="4vCPUs";;
        *) HARDWARE="8vCPUs";;
    esac
    
    echo ""
    read -p "Expected events per second (EPS) [10000]: " EXPECTED_EPS
    EXPECTED_EPS=${EXPECTED_EPS:-10000}
    
    echo ""
    echo "Select primary protocol:"
    echo "1) UDP (faster, best for high volume)"
    echo "2) TCP (reliable, guaranteed delivery)"
    echo ""
    read -p "Select protocol [1]: " proto_choice
    proto_choice=${proto_choice:-1}
    
    case "$proto_choice" in
        1) PROTOCOL="udp";;
        2) PROTOCOL="tcp";;
        *) PROTOCOL="udp";;
    esac
    
    # Apply hardware-based configuration
    apply_hardware_config "$HARDWARE" "$PROTOCOL" "$EXPECTED_EPS"
    
    # Still need Splunk configuration
    echo ""
    printf "${GREEN}=== Splunk Configuration ===${NC}\n"
    read_hec_url
    read_hec_token
    TLS_VERIFY=$(ask_yes_no "Verify SSL/TLS certificates?" "yes")
    
    # Skip to generation
    MODE="hardware"
    
else
    # Custom interactive mode (existing flow)
    MODE="custom"
    echo ""
    printf "${GREEN}=== Splunk Configuration ===${NC}\n"
fi

if [ "$MODE" = "custom" ]; then

# Splunk configuration
read_hec_url
read_hec_token
TLS_VERIFY=$(ask_yes_no "Verify SSL/TLS certificates?" "yes")

echo ""
printf "${GREEN}=== Performance Configuration ===${NC}\n"

# Protocol selection
echo ""
echo "Protocol optimisation:"
echo "1) UDP only (faster, may lose messages)"
echo "2) TCP only (reliable, slower)"
echo "3) Both UDP and TCP (default)"
read -p "Select protocol [3]: " protocol_choice
protocol_choice=${protocol_choice:-3}
case "$protocol_choice" in
    1) PROTOCOL="udp";;
    2) PROTOCOL="tcp";;
    3) PROTOCOL="both";;
    *) PROTOCOL="both";;
esac

# Advanced UDP options
echo ""
printf "${GREEN}=== Advanced UDP Options ===${NC}\n"

# UDP fetch limit overrides
if [ "$PROTOCOL" = "udp" ] || [ "$PROTOCOL" = "both" ]; then
    ADJUST_FETCH_LIMIT=$(ask_yes_no "Adjust fetch limit for UDP" "no")

    if [ "$ADJUST_FETCH_LIMIT" = "yes" ]; then
        read -p "UDP fetch limit [$SC4S_SOURCE_UDP_FETCH_LIMIT]: " input_udp_fetch_limit
        SC4S_SOURCE_UDP_FETCH_LIMIT=${input_udp_fetch_limit:-$SC4S_SOURCE_UDP_FETCH_LIMIT}
    fi
fi

# UDP listen socket overrides
if [ "$PROTOCOL" = "udp" ] || [ "$PROTOCOL" = "both" ]; then
    ADJUST_LISTEN_SOCKETS=$(ask_yes_no "Adjust number of UDP listen sockets?" "no")

    if [ "$ADJUST_LISTEN_SOCKETS" = "yes" ]; then
        read -p "UDP listen sockets [$SC4S_SOURCE_LISTEN_UDP_SOCKETS]: " input_udp_sockets
        SC4S_SOURCE_LISTEN_UDP_SOCKETS=${input_udp_sockets:-$SC4S_SOURCE_LISTEN_UDP_SOCKETS}
    fi
fi

# UDP receiving buffer overrides
if [ "$PROTOCOL" = "udp" ] || [ "$PROTOCOL" = "both" ]; then
    read -p "Tune UDP receiving buffer (-1 to skip, default 17039360 bytes) [$SC4S_SOURCE_UDP_SO_RCVBUFF]: " input_udp_rcvbuff
    SC4S_SOURCE_UDP_SO_RCVBUFF=${input_udp_rcvbuff:-$SC4S_SOURCE_UDP_SO_RCVBUFF}
fi

# UDP eBPF options
if [ "$PROTOCOL" = "udp" ] || [ "$PROTOCOL" = "both" ]; then
    SC4S_ENABLE_EBPF=$(ask_yes_no "Enable eBPF?" "$SC4S_ENABLE_EBPF")
    if [ "$SC4S_ENABLE_EBPF" = "yes" ]; then
        read -p "Number of eBPF sockets [4]: " input_ebpf_sockets
        SC4S_EBPF_NO_SOCKETS=${input_ebpf_sockets:-4}
    fi
fi

# Advanced TCP options
echo ""
printf "${GREEN}=== Advanced TCP Options ===${NC}\n"

# TCP receiving buffer overrides
if [ "$PROTOCOL" = "tcp" ] || [ "$PROTOCOL" = "both" ]; then
    read -p "Tune TCP receiving buffer (-1 to skip, default 17039360 bytes) [$SC4S_SOURCE_TCP_SO_RCVBUFF]: " input_tcp_rcvbuff
    SC4S_SOURCE_TCP_SO_RCVBUFF=${input_tcp_rcvbuff:-$SC4S_SOURCE_TCP_SO_RCVBUFF}
fi

# TCP parallelization
if [ "$PROTOCOL" = "tcp" ] || [ "$PROTOCOL" = "both" ]; then
    PARALLELIZE=$(ask_yes_no "Enable TCP parallelization?" "$PARALLELIZE")
    if [ "$PARALLELIZE" = "yes" ]; then
        read -p "Number of partitions for parallelization [4]: " input_partitions
        SC4S_PARALLELIZE_NO_PARTITION=${input_partitions:-4}
    fi
fi

# TCP IW settings
if [ "$PROTOCOL" = "tcp" ] || [ "$PROTOCOL" = "both" ]; then
    SC4S_SOURCE_TCP_IW_USE=$(ask_yes_no "Tune static window size?" "$SC4S_SOURCE_TCP_IW_USE")
    if [ "$SC4S_SOURCE_TCP_IW_USE" = "yes" ]; then
        read -p "Input window size [1000000]: " input_iw_size
        SC4S_SOURCE_TCP_IW_SIZE=${input_iw_size:-1000000}
    fi
fi

# Disk Buffer Configuration
echo ""
printf "${GREEN}=== Disk Buffer Configuration ===${NC}\n"

ADJUST_DISKBUFF=$(ask_yes_no "Adjust disk buffer settings?" "no")

if [ "$ADJUST_DISKBUFF" = "yes" ]; then
    SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE=$(ask_yes_no "Enable local disk buffering?" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE")

    if [ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE" = "yes" ]; then
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE=$(ask_yes_no "Enable reliable disk buffering (recommended: no for normal buffering)?" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE")
        
        if [ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE" = "yes" ]; then
            read -p "Worker memory buffer size in bytes (for reliable buffering) [$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE]: " input_membufsize
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=${input_membufsize:-$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE}
        else
            read -p "Worker memory buffer size in message count (for normal buffering) [$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH]: " input_membuflength
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH=${input_membuflength:-$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH}
        fi
        
        read -p "Disk buffer size in bytes (default 50GB per worker) [$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE]: " input_diskbufsize
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=${input_diskbufsize:-$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE}
    fi
fi

fi  # End of custom mode

# Output file
echo ""
read -p "Output filename [$OUTPUT_FILE]: " input_output
OUTPUT_FILE=${input_output:-$OUTPUT_FILE}

while [ -f "$OUTPUT_FILE" ]; do
    printf "${YELLOW}Warning: '$OUTPUT_FILE' already exists.${NC}\n"
    OVERWRITE=$(ask_yes_no "Overwrite it?" "no")
    if [ "$OVERWRITE" = "yes" ]; then
        break
    fi
    read -p "Enter a different filename: " OUTPUT_FILE
    if [ -z "$OUTPUT_FILE" ]; then
        printf "${RED}No filename provided. Aborting.${NC}\n"
        exit 1
    fi
done

# Build configuration into variable
if [ "$MODE" = "hardware" ]; then
    MODE_INFO="Mode: Hardware-based ($HARDWARE)"
else
    MODE_INFO="Mode: Custom configuration"
fi

CONFIG="# SC4S Configuration - Generated by configuration tool
# $MODE_INFO
# Expected EPS: $EXPECTED_EPS
# Protocol: $PROTOCOL
# Generated on: $(date)

# === Splunk HEC Configuration ===
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$SPLUNK_URL
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=$HEC_TOKEN"

if [ "$TLS_VERIFY" = "no" ]; then
    CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no"
fi

CONFIG="$CONFIG

# === Performance Configuration ==="

# UDP configuration
if [ "$PROTOCOL" = "udp" ] || [ "$PROTOCOL" = "both" ]; then
    if [ "$ADJUST_FETCH_LIMIT" = "yes" ] && [ -n "$SC4S_SOURCE_UDP_FETCH_LIMIT" ]; then
        CONFIG="$CONFIG
SC4S_SOURCE_UDP_FETCH_LIMIT=$SC4S_SOURCE_UDP_FETCH_LIMIT"
    fi

    if [ "$ADJUST_LISTEN_SOCKETS" = "yes" ]; then
        CONFIG="$CONFIG
SC4S_SOURCE_LISTEN_UDP_SOCKETS=$SC4S_SOURCE_LISTEN_UDP_SOCKETS"
    fi

    if [ "$SC4S_SOURCE_UDP_SO_RCVBUFF" -gt 0 ]; then
        CONFIG="$CONFIG
SC4S_SOURCE_UDP_SO_RCVBUFF=$SC4S_SOURCE_UDP_SO_RCVBUFF"
    fi

    if [ "$SC4S_ENABLE_EBPF" = "yes" ]; then
        CONFIG="$CONFIG
SC4S_ENABLE_EBPF=$SC4S_ENABLE_EBPF
SC4S_EBPF_NO_SOCKETS=$SC4S_EBPF_NO_SOCKETS"
    fi
fi

# TCP configuration
if [ "$PROTOCOL" = "tcp" ] || [ "$PROTOCOL" = "both" ]; then
    if [ "$SC4S_SOURCE_TCP_SO_RCVBUFF" -gt 0 ]; then
        CONFIG="$CONFIG
SC4S_SOURCE_TCP_SO_RCVBUFF=$SC4S_SOURCE_TCP_SO_RCVBUFF"
    fi

    if [ "$PARALLELIZE" = "yes" ]; then
        CONFIG="$CONFIG
SC4S_ENABLE_PARALLELIZE=yes
SC4S_PARALLELIZE_NO_PARTITION=$SC4S_PARALLELIZE_NO_PARTITION"
    fi

    if [ "$SC4S_SOURCE_TCP_IW_USE" = "yes" ]; then
        CONFIG="$CONFIG
SC4S_SOURCE_TCP_IW_SIZE=$SC4S_SOURCE_TCP_IW_SIZE"
    fi
fi

# Disk buffer configuration
if [ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE" = "yes" ] && [ "$ADJUST_DISKBUFF" = "yes" ]; then
    CONFIG="$CONFIG

# === Disk buffer Configuration ===
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE"

    if [ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE" = "yes" ]; then
        CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE"
    else
        CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFLENGTH"
    fi

    CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE"
fi

# Review and confirm
echo ""
printf "${BLUE}================================================${NC}\n"
printf "${BLUE}    Review Configuration${NC}\n"
printf "${BLUE}================================================${NC}\n"
echo ""
echo "$CONFIG"
echo ""
printf "${BLUE}================================================${NC}\n"
echo ""

CONFIRM=$(ask_yes_no "Write this configuration to '$OUTPUT_FILE'?" "yes")
if [ "$CONFIRM" != "yes" ]; then
    printf "${YELLOW}Aborted. No file was written.${NC}\n"
    exit 0
fi

# Write to file
echo "$CONFIG" > "$OUTPUT_FILE"

echo ""
printf "${GREEN}Configuration saved successfully!${NC}\n"
printf "File: ${YELLOW}$OUTPUT_FILE${NC}\n"
echo ""

# === Final recommendations ===
if [ "$SC4S_SOURCE_UDP_SO_RCVBUFF" -gt 0 ] || [ "$SC4S_SOURCE_TCP_SO_RCVBUFF" -gt 0 ]; then
echo ""
printf "${YELLOW}Note: You may need to adjust your system's UDP/TCP receiving buffer settings to match the configured values.${NC}\n"
echo "You can modify /etc/sysctl.conf following this documentation:"
echo "https://splunk.github.io/splunk-connect-for-syslog/main/gettingstarted/getting-started-runtime-configuration/#tune-your-receive-buffer"
fi


if [ "$SC4S_ENABLE_EBPF" = "yes" ]; then
echo ""
printf "${YELLOW}Note: Enabling eBPF may require additional system permissions.${NC}\n"
echo "Ensure that your system supports eBPF and that the necessary capabilities are granted to the SC4S process or container. Read more here: "
echo "https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#about-ebpf"
fi

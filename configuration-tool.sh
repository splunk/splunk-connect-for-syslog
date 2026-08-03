#!/bin/bash
# filepath: configuration-tool.sh

# SC4S Configuration Tool
# Generates a customized env_file based on user requirements

set -e

# Help flag
if [[ "${1:-}" = "--help" || "${1:-}" = "-h" ]]; then
    cat << 'EOF'
SC4S Configuration Tool

Interactively generates an env_file for Splunk Connect for Syslog (SC4S).

Usage: ./configuration-tool.sh [OPTIONS]

Options:
  -h, --help    Show this help message and exit
  -o, --output  Set output filename (default: env_file)

Non-interactive mode (SC4S_NON_INTERACTIVE=1):
  Set SC4S_NON_INTERACTIVE=1 and provide inputs through environment variables.
  The generated env_file is written to stdout and errors are written to stderr.

  Required:
    SC4S_HEC_URL         Splunk HEC URL
    SC4S_HEC_TOKEN       Splunk HEC token in UUID format

  Optional:
    SC4S_TLS_VERIFY                yes|no (default: yes)
    SC4S_PROTOCOL                  udp|tcp|both (default: both)
    SC4S_MODE                      1=custom, 2=hardware (default: 1)
    SC4S_HARDWARE                  16vCPUs|8vCPUs|4vCPUs (default: 8vCPUs)
    SC4S_EXPECTED_EPS              non-negative integer (default: 1000)
    SC4S_DEFAULT_TIMEZONE          Region/City timezone (default: unset)
    SC4S_ADJUST_FETCH_LIMIT        yes|no (default: no)
    SC4S_SOURCE_UDP_FETCH_LIMIT    integer (default: 1000)
    SC4S_ADJUST_LISTEN_SOCKETS     yes|no (default: no)
    SC4S_SOURCE_LISTEN_UDP_SOCKETS integer (default: 2)
    SC4S_SOURCE_UDP_SO_RCVBUFF     integer (default: -1)
    SC4S_ENABLE_EBPF               yes|no (default: no)
    SC4S_EBPF_NO_SOCKETS           integer (default: 4)
    SC4S_SOURCE_UDP_IW_USE         yes|no (default: no)
    SC4S_SOURCE_UDP_IW_SIZE        integer (default: 250000)
    SC4S_SOURCE_TCP_SO_RCVBUFF     integer (default: -1)
    SC4S_PARALLELIZE               yes|no (default: no)
    SC4S_PARALLELIZE_NO_PARTITION  integer (default: 4)
    SC4S_SOURCE_TCP_IW_USE         yes|no (default: no)
    SC4S_SOURCE_TCP_IW_SIZE        integer (default: 20000000)
    SC4S_ADJUST_DISKBUFF           yes|no (default: no)
    SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE       yes|no (default: yes)
    SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE     yes|no (default: no)
    SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE   integer (default: 163840000)
    SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE  integer (default: 53687091200)

Modes:
  1) Custom        Step-by-step configuration of all settings
  2) Hardware      Auto-tuned settings based on your hardware and expected EPS

The tool will prompt for:
  - Splunk HEC URL and token (with validation)
  - Protocol selection (UDP/TCP/both)
  - Performance tuning (buffer sizes, eBPF, parallelization)
  - Disk buffer settings

A review step is shown before writing the file.

Documentation: https://splunk.github.io/splunk-connect-for-syslog/
EOF
    exit 0
fi

# Parse optional flags
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            if [[ -z "${2:-}" ]]; then
                echo "Error: --output requires a filename argument." >&2
                echo "Usage: ./configuration-tool.sh -o <filename>" >&2
                exit 1
            fi
            OUTPUT_FILE="$2"; shift 2;;
        *) echo "Unknown option: $1. Use --help for usage." >&2; exit 1;;
    esac
done

# Preserve non-interactive inputs whose names are also used as internal shell
# variables. The interactive defaults below intentionally remain unchanged.
NI_DEFAULT_TIMEZONE="${SC4S_DEFAULT_TIMEZONE:-}"
NI_UDP_LISTEN_SOCKETS="${SC4S_SOURCE_LISTEN_UDP_SOCKETS:-}"
NI_UDP_FETCH_LIMIT="${SC4S_SOURCE_UDP_FETCH_LIMIT:-}"
NI_ENABLE_EBPF="${SC4S_ENABLE_EBPF:-}"
NI_EBPF_SOCKETS="${SC4S_EBPF_NO_SOCKETS:-}"
NI_PARALLELIZE_PARTITIONS="${SC4S_PARALLELIZE_NO_PARTITION:-}"
NI_UDP_IW_USE="${SC4S_SOURCE_UDP_IW_USE:-}"
NI_UDP_IW_SIZE="${SC4S_SOURCE_UDP_IW_SIZE:-}"
NI_TCP_IW_USE="${SC4S_SOURCE_TCP_IW_USE:-}"
NI_TCP_IW_SIZE="${SC4S_SOURCE_TCP_IW_SIZE:-}"
NI_UDP_RCVBUFF="${SC4S_SOURCE_UDP_SO_RCVBUFF:-}"
NI_TCP_RCVBUFF="${SC4S_SOURCE_TCP_SO_RCVBUFF:-}"
NI_DISKBUFF_ENABLE="${SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE:-}"
NI_DISKBUFF_RELIABLE="${SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE:-}"
NI_DISKBUFF_MEMBUFSIZE="${SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE:-}"
NI_DISKBUFF_DISKBUFSIZE="${SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE:-}"

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Initialize variables
OUTPUT_FILE=${OUTPUT_FILE:-"env_file"}
SPLUNK_URL=""
HEC_TOKEN=""
TLS_VERIFY="yes"
EXPECTED_EPS=1000
PROTOCOL="both"

ADJUST_FETCH_LIMIT="no"
ADJUST_LISTEN_SOCKETS="no"
ADJUST_DISKBUFF="no"
SC4S_SOURCE_LISTEN_UDP_SOCKETS=2
SC4S_SOURCE_UDP_FETCH_LIMIT=1000
SC4S_ENABLE_EBPF="no"
SC4S_EBPF_NO_SOCKETS=4

PARALLELIZE="no"
SC4S_PARALLELIZE_NO_PARTITION=4
SC4S_SOURCE_UDP_IW_USE="no"
SC4S_SOURCE_UDP_IW_SIZE=250000
SC4S_SOURCE_TCP_IW_USE="no"
SC4S_SOURCE_TCP_IW_SIZE=20000000

SC4S_SOURCE_UDP_SO_RCVBUFF=-1
SC4S_SOURCE_TCP_SO_RCVBUFF=-1

SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE="yes"
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE="no"
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=163840000
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=53687091200

SC4S_DEFAULT_TIMEZONE=""

# Validate HEC URL: must start with http:// or https://, have a hostname, and optionally a port
validate_hec_url() {
    local url="$1"
    if [[ "$url" == *$'\n'* || "$url" == *$'\r'* ]]; then
        return 1
    fi
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
        if [[ -z "$input" ]]; then
            printf "${RED}HEC URL cannot be empty.${NC}\n"
        elif validate_hec_url "$input"; then
            SPLUNK_URL="$input"
            break
        else
            printf "${RED}Invalid URL format. Must start with http:// or https:// followed by a hostname.${NC}\n"
            printf "${YELLOW}Example: https://splunk.example.com:8088${NC}\n"
        fi
    done
    return 0
}

# Prompt for HEC token with validation, retries until valid
read_hec_token() {
    local input
    while true; do
        read -p "Enter your Splunk HEC Token: " input
        if [[ -z "$input" ]]; then
            printf "${RED}HEC Token cannot be empty.${NC}\n"
        elif validate_hec_token "$input"; then
            HEC_TOKEN="$input"
            break
        else
            printf "${RED}Invalid token format. Expected a UUID (e.g., 12345678-1234-1234-1234-123456789abc).${NC}\n"
        fi
    done
    return 0
}

# Prompt for a numeric value with validation; echoes the result for capture via $()
read_numeric() {
    local prompt="$1"
    local default="$2"
    local input
    while true; do
        printf "%s [%s]: " "$prompt" "$default" >&2
        read input </dev/tty
        input=${input:-$default}
        if [[ "$input" =~ ^-?[0-9]+$ ]]; then
            echo "$input"
            return
        fi
        printf "${RED}Invalid input. Please enter a number.${NC}\n" >&2
    done
}

# Function to ask yes/no questions
ask_yes_no() {
    local question="$1"
    local default="$2"
    local response
    
    while true; do
        if [[ "$default" = "yes" ]]; then
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
    return 0
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
            
            if [[ ( "$protocol" = "udp" || "$protocol" = "both" ) && "$expected_eps" -gt 35000 ]]; then
                ADJUST_FETCH_LIMIT="yes"
                SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                SC4S_ENABLE_EBPF="yes"
                SC4S_EBPF_NO_SOCKETS=16
                ADJUST_LISTEN_SOCKETS="yes"
                SC4S_SOURCE_LISTEN_UDP_SOCKETS=64
                SC4S_SOURCE_UDP_SO_RCVBUFF=536870912
            fi
            if [[ ( "$protocol" = "tcp" || "$protocol" = "both" ) && "$expected_eps" -gt 50000 ]]; then
                PARALLELIZE="yes"
                SC4S_PARALLELIZE_NO_PARTITION=8
                SC4S_SOURCE_TCP_SO_RCVBUFF=536870912
            fi
            ;;
            
        "8vCPUs")
            # 8 vCPUs, 32 GB RAM
            
            if [[ ( "$protocol" = "udp" || "$protocol" = "both" ) && "$expected_eps" -gt 25000 ]]; then
                ADJUST_FETCH_LIMIT="yes"
                SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                SC4S_ENABLE_EBPF="yes"
                SC4S_EBPF_NO_SOCKETS=16
                ADJUST_LISTEN_SOCKETS="yes"
                SC4S_SOURCE_LISTEN_UDP_SOCKETS=32
                SC4S_SOURCE_UDP_SO_RCVBUFF=268435456
            fi
            if [[ ( "$protocol" = "tcp" || "$protocol" = "both" ) && "$expected_eps" -gt 30000 ]]; then
                PARALLELIZE="yes"
                SC4S_PARALLELIZE_NO_PARTITION=8
                SC4S_SOURCE_TCP_SO_RCVBUFF=268435456
            fi
            ;;
            
        "4vCPUs")
            # 4 vCPUs, 16 GB RAM
            
            if [[ ( "$protocol" = "udp" || "$protocol" = "both" ) && "$expected_eps" -gt 10000 ]]; then
                ADJUST_FETCH_LIMIT="yes"
                SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                SC4S_ENABLE_EBPF="yes"
                SC4S_EBPF_NO_SOCKETS=8
                ADJUST_LISTEN_SOCKETS="yes"
                SC4S_SOURCE_LISTEN_UDP_SOCKETS=16
                SC4S_SOURCE_UDP_SO_RCVBUFF=268435456
            fi
            if [[ ( "$protocol" = "tcp" || "$protocol" = "both" ) && "$expected_eps" -gt 20000 ]]; then
                PARALLELIZE="yes"
                SC4S_PARALLELIZE_NO_PARTITION=4
                SC4S_SOURCE_TCP_SO_RCVBUFF=268435456
            fi
            ;;

        *)
            # default case

            if [[ ( "$protocol" = "udp" || "$protocol" = "both" ) && "$expected_eps" -gt 10000 ]]; then
                ADJUST_FETCH_LIMIT="yes"
                SC4S_SOURCE_UDP_FETCH_LIMIT=1000000
                SC4S_ENABLE_EBPF="yes"
                SC4S_EBPF_NO_SOCKETS=8
                ADJUST_LISTEN_SOCKETS="yes"
                SC4S_SOURCE_LISTEN_UDP_SOCKETS=16
                SC4S_SOURCE_UDP_SO_RCVBUFF=268435456
            fi
            if [[ ( "$protocol" = "tcp" || "$protocol" = "both" ) && "$expected_eps" -gt 20000 ]]; then
                PARALLELIZE="yes"
                SC4S_PARALLELIZE_NO_PARTITION=4
                SC4S_SOURCE_TCP_SO_RCVBUFF=268435456
            fi
            ;;
    esac
    return 0
}

# Build the env_file from the collected settings. Both interactive and
# non-interactive modes call this function so configuration output has one
# source of truth.
build_config() {
    if [[ "$mode_choice" = "2" ]]; then
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

    if [[ "$TLS_VERIFY" = "no" ]]; then
        CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no"
    fi

    if [[ -n "$SC4S_DEFAULT_TIMEZONE" ]]; then
        CONFIG="$CONFIG

# === Timezone Configuration ===
SC4S_DEFAULT_TIMEZONE=$SC4S_DEFAULT_TIMEZONE"
    fi

    CONFIG="$CONFIG

# === Performance Configuration ==="

    if [[ "$PROTOCOL" = "udp" || "$PROTOCOL" = "both" ]]; then
        if [[ "$ADJUST_FETCH_LIMIT" = "yes" && -n "$SC4S_SOURCE_UDP_FETCH_LIMIT" ]]; then
            CONFIG="$CONFIG
SC4S_SOURCE_UDP_FETCH_LIMIT=$SC4S_SOURCE_UDP_FETCH_LIMIT"
        fi

        if [[ "$ADJUST_LISTEN_SOCKETS" = "yes" ]]; then
            CONFIG="$CONFIG
SC4S_SOURCE_LISTEN_UDP_SOCKETS=$SC4S_SOURCE_LISTEN_UDP_SOCKETS"
        fi

        if [[ "$SC4S_SOURCE_UDP_SO_RCVBUFF" -gt 0 ]]; then
            CONFIG="$CONFIG
SC4S_SOURCE_UDP_SO_RCVBUFF=$SC4S_SOURCE_UDP_SO_RCVBUFF"
        fi

        if [[ "$SC4S_ENABLE_EBPF" = "yes" ]]; then
            CONFIG="$CONFIG
SC4S_ENABLE_EBPF=$SC4S_ENABLE_EBPF
SC4S_EBPF_NO_SOCKETS=$SC4S_EBPF_NO_SOCKETS"
        fi

        if [[ "$SC4S_SOURCE_UDP_IW_USE" = "yes" ]]; then
            CONFIG="$CONFIG
SC4S_SOURCE_UDP_IW_USE=yes
SC4S_SOURCE_UDP_IW_SIZE=$SC4S_SOURCE_UDP_IW_SIZE"
        fi
    fi

    if [[ "$PROTOCOL" = "tcp" || "$PROTOCOL" = "both" ]]; then
        if [[ "$SC4S_SOURCE_TCP_SO_RCVBUFF" -gt 0 ]]; then
            CONFIG="$CONFIG
SC4S_SOURCE_TCP_SO_RCVBUFF=$SC4S_SOURCE_TCP_SO_RCVBUFF"
        fi

        if [[ "$PARALLELIZE" = "yes" ]]; then
            CONFIG="$CONFIG
SC4S_ENABLE_PARALLELIZE=yes
SC4S_PARALLELIZE_NO_PARTITION=$SC4S_PARALLELIZE_NO_PARTITION"
        fi

        if [[ "$SC4S_SOURCE_TCP_IW_USE" = "yes" ]]; then
            CONFIG="$CONFIG
SC4S_SOURCE_TCP_IW_SIZE=$SC4S_SOURCE_TCP_IW_SIZE"
        fi
    fi

    if [[ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE" = "yes" && "$ADJUST_DISKBUFF" = "yes" ]]; then
        CONFIG="$CONFIG

# === Disk buffer Configuration ===
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE"

        if [[ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE" = "yes" ]]; then
            CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE"
        fi

        CONFIG="$CONFIG
SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE"
    fi
}

require_yes_no() {
    local name="$1"
    local value="$2"
    if [[ ! "$value" =~ ^(yes|no)$ ]]; then
        echo "Error: $name must be yes or no." >&2
        return 1
    fi
}

require_integer() {
    local name="$1"
    local value="$2"
    if [[ ! "$value" =~ ^-?[0-9]+$ ]]; then
        echo "Error: $name must be an integer." >&2
        return 1
    fi
}

load_non_interactive() {
    SPLUNK_URL="${SC4S_HEC_URL:-}"
    HEC_TOKEN="${SC4S_HEC_TOKEN:-}"
    TLS_VERIFY="${SC4S_TLS_VERIFY:-yes}"
    PROTOCOL="${SC4S_PROTOCOL:-both}"
    EXPECTED_EPS="${SC4S_EXPECTED_EPS:-1000}"
    SC4S_DEFAULT_TIMEZONE="${NI_DEFAULT_TIMEZONE:-}"

    if [[ -z "$SPLUNK_URL" ]]; then
        echo "Error: SC4S_HEC_URL is required in non-interactive mode." >&2
        return 1
    fi
    if ! validate_hec_url "$SPLUNK_URL"; then
        echo "Error: invalid SC4S_HEC_URL '$SPLUNK_URL'." >&2
        return 1
    fi
    if [[ -z "$HEC_TOKEN" ]]; then
        echo "Error: SC4S_HEC_TOKEN is required in non-interactive mode." >&2
        return 1
    fi
    if ! validate_hec_token "$HEC_TOKEN"; then
        echo "Error: invalid SC4S_HEC_TOKEN UUID." >&2
        return 1
    fi
    if [[ ! "$PROTOCOL" =~ ^(udp|tcp|both)$ ]]; then
        echo "Error: SC4S_PROTOCOL must be udp, tcp, or both." >&2
        return 1
    fi
    if [[ ! "$EXPECTED_EPS" =~ ^[0-9]+$ ]]; then
        echo "Error: SC4S_EXPECTED_EPS must be a non-negative integer." >&2
        return 1
    fi
    require_yes_no "SC4S_TLS_VERIFY" "$TLS_VERIFY"
    if [[ -n "$SC4S_DEFAULT_TIMEZONE" && ! "$SC4S_DEFAULT_TIMEZONE" =~ ^[A-Za-z_]+/[A-Za-z_]+(/[A-Za-z_]+)?$ ]]; then
        echo "Error: invalid SC4S_DEFAULT_TIMEZONE '$SC4S_DEFAULT_TIMEZONE'." >&2
        return 1
    fi

    case "${SC4S_MODE:-1}" in
        1)
            mode_choice=1
            ADJUST_FETCH_LIMIT="${SC4S_ADJUST_FETCH_LIMIT:-no}"
            SC4S_SOURCE_UDP_FETCH_LIMIT="${NI_UDP_FETCH_LIMIT:-1000}"
            ADJUST_LISTEN_SOCKETS="${SC4S_ADJUST_LISTEN_SOCKETS:-no}"
            SC4S_SOURCE_LISTEN_UDP_SOCKETS="${NI_UDP_LISTEN_SOCKETS:-2}"
            SC4S_SOURCE_UDP_SO_RCVBUFF="${NI_UDP_RCVBUFF:--1}"
            SC4S_ENABLE_EBPF="${NI_ENABLE_EBPF:-no}"
            SC4S_EBPF_NO_SOCKETS="${NI_EBPF_SOCKETS:-4}"
            SC4S_SOURCE_UDP_IW_USE="${NI_UDP_IW_USE:-no}"
            SC4S_SOURCE_UDP_IW_SIZE="${NI_UDP_IW_SIZE:-250000}"
            SC4S_SOURCE_TCP_SO_RCVBUFF="${NI_TCP_RCVBUFF:--1}"
            PARALLELIZE="${SC4S_PARALLELIZE:-no}"
            SC4S_PARALLELIZE_NO_PARTITION="${NI_PARALLELIZE_PARTITIONS:-4}"
            SC4S_SOURCE_TCP_IW_USE="${NI_TCP_IW_USE:-no}"
            SC4S_SOURCE_TCP_IW_SIZE="${NI_TCP_IW_SIZE:-20000000}"
            ADJUST_DISKBUFF="${SC4S_ADJUST_DISKBUFF:-no}"
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE="${NI_DISKBUFF_ENABLE:-yes}"
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE="${NI_DISKBUFF_RELIABLE:-no}"
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE="${NI_DISKBUFF_MEMBUFSIZE:-163840000}"
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE="${NI_DISKBUFF_DISKBUFSIZE:-53687091200}"

            require_yes_no "SC4S_ADJUST_FETCH_LIMIT" "$ADJUST_FETCH_LIMIT"
            require_yes_no "SC4S_ADJUST_LISTEN_SOCKETS" "$ADJUST_LISTEN_SOCKETS"
            require_yes_no "SC4S_ENABLE_EBPF" "$SC4S_ENABLE_EBPF"
            require_yes_no "SC4S_SOURCE_UDP_IW_USE" "$SC4S_SOURCE_UDP_IW_USE"
            require_yes_no "SC4S_PARALLELIZE" "$PARALLELIZE"
            require_yes_no "SC4S_SOURCE_TCP_IW_USE" "$SC4S_SOURCE_TCP_IW_USE"
            require_yes_no "SC4S_ADJUST_DISKBUFF" "$ADJUST_DISKBUFF"
            require_yes_no "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE"
            require_yes_no "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE"

            require_integer "SC4S_SOURCE_UDP_FETCH_LIMIT" "$SC4S_SOURCE_UDP_FETCH_LIMIT"
            require_integer "SC4S_SOURCE_LISTEN_UDP_SOCKETS" "$SC4S_SOURCE_LISTEN_UDP_SOCKETS"
            require_integer "SC4S_SOURCE_UDP_SO_RCVBUFF" "$SC4S_SOURCE_UDP_SO_RCVBUFF"
            require_integer "SC4S_EBPF_NO_SOCKETS" "$SC4S_EBPF_NO_SOCKETS"
            require_integer "SC4S_SOURCE_UDP_IW_SIZE" "$SC4S_SOURCE_UDP_IW_SIZE"
            require_integer "SC4S_SOURCE_TCP_SO_RCVBUFF" "$SC4S_SOURCE_TCP_SO_RCVBUFF"
            require_integer "SC4S_PARALLELIZE_NO_PARTITION" "$SC4S_PARALLELIZE_NO_PARTITION"
            require_integer "SC4S_SOURCE_TCP_IW_SIZE" "$SC4S_SOURCE_TCP_IW_SIZE"
            require_integer "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE"
            require_integer "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE"
            ;;
        2)
            mode_choice=2
            HARDWARE="${SC4S_HARDWARE:-8vCPUs}"
            if [[ ! "$HARDWARE" =~ ^(16vCPUs|8vCPUs|4vCPUs)$ ]]; then
                echo "Error: invalid SC4S_HARDWARE '$HARDWARE'." >&2
                return 1
            fi
            apply_hardware_config "$HARDWARE" "$PROTOCOL" "$EXPECTED_EPS" >/dev/null
            ;;
        *)
            echo "Error: SC4S_MODE must be 1 or 2." >&2
            return 1
            ;;
    esac
}

if [[ "${SC4S_NON_INTERACTIVE:-}" = "1" ]]; then
    load_non_interactive
    build_config
    printf "%s\n" "$CONFIG"
    exit 0
fi

echo ""
printf "${BLUE}================================================${NC}\n"
printf "${BLUE}    SC4S Configuration Tool${NC}\n"
printf "${BLUE}================================================${NC}\n"
echo ""
echo "This tool will help you generate an optimized SC4S configuration"
echo "based on your requirements."
echo ""

# Mode selection
printf "${GREEN}=== Configuration Mode ===${NC}\n"
echo ""
echo "Choose configuration mode:"
echo "1) Custom configuration (default)"
echo "2) Hardware-based configuration (estimate based on hardware and events per second)"
echo ""
read -p "Select mode [1]: " mode_choice
mode_choice=${mode_choice:-1}

if [[ "$mode_choice" = "1" || "$mode_choice" = "" ]]; then
    # Custom interactive mode
    
    echo ""
    printf "${GREEN}=== Splunk Configuration ===${NC}\n"

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
    if [[ "$PROTOCOL" = "udp" || "$PROTOCOL" = "both" ]]; then
        echo ""
        printf "${GREEN}=== Advanced UDP Options ===${NC}\n"

        ADJUST_FETCH_LIMIT=$(ask_yes_no "Adjust fetch limit for UDP" "no")
        if [[ "$ADJUST_FETCH_LIMIT" = "yes" ]]; then
            SC4S_SOURCE_UDP_FETCH_LIMIT=$(read_numeric "UDP fetch limit" "$SC4S_SOURCE_UDP_FETCH_LIMIT")
        fi

        ADJUST_LISTEN_SOCKETS=$(ask_yes_no "Adjust number of UDP listen sockets?" "no")
        if [[ "$ADJUST_LISTEN_SOCKETS" = "yes" ]]; then
            SC4S_SOURCE_LISTEN_UDP_SOCKETS=$(read_numeric "UDP listen sockets" "$SC4S_SOURCE_LISTEN_UDP_SOCKETS")
        fi

        SC4S_SOURCE_UDP_SO_RCVBUFF=$(read_numeric "Tune UDP receiving buffer (-1 to skip, default 17039360 bytes)" "$SC4S_SOURCE_UDP_SO_RCVBUFF")

        SC4S_ENABLE_EBPF=$(ask_yes_no "Enable eBPF?" "$SC4S_ENABLE_EBPF")
        if [[ "$SC4S_ENABLE_EBPF" = "yes" ]]; then
            SC4S_EBPF_NO_SOCKETS=$(read_numeric "Number of eBPF sockets" "4")
        fi

        SC4S_SOURCE_UDP_IW_USE=$(ask_yes_no "Tune UDP static window size?" "$SC4S_SOURCE_UDP_IW_USE")
        if [[ "$SC4S_SOURCE_UDP_IW_USE" = "yes" ]]; then
            SC4S_SOURCE_UDP_IW_SIZE=$(read_numeric "UDP input window size" "1000000")
        fi
    fi

    # Advanced TCP options
    if [[ "$PROTOCOL" = "tcp" || "$PROTOCOL" = "both" ]]; then
        echo ""
        printf "${GREEN}=== Advanced TCP Options ===${NC}\n"

        SC4S_SOURCE_TCP_SO_RCVBUFF=$(read_numeric "Tune TCP receiving buffer (-1 to skip, default 17039360 bytes)" "$SC4S_SOURCE_TCP_SO_RCVBUFF")

        PARALLELIZE=$(ask_yes_no "Enable TCP parallelization?" "$PARALLELIZE")
        if [[ "$PARALLELIZE" = "yes" ]]; then
            SC4S_PARALLELIZE_NO_PARTITION=$(read_numeric "Number of partitions for parallelization" "4")
        fi

        SC4S_SOURCE_TCP_IW_USE=$(ask_yes_no "Tune static window size?" "$SC4S_SOURCE_TCP_IW_USE")
        if [[ "$SC4S_SOURCE_TCP_IW_USE" = "yes" ]]; then
            SC4S_SOURCE_TCP_IW_SIZE=$(read_numeric "Input window size" "1000000")
        fi
    fi

    # Disk Buffer Configuration
    echo ""
    printf "${GREEN}=== Disk Buffer Configuration ===${NC}\n"

    ADJUST_DISKBUFF=$(ask_yes_no "Adjust disk buffer settings?" "no")
    if [[ "$ADJUST_DISKBUFF" = "yes" ]]; then
        SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE=$(ask_yes_no "Enable local disk buffering?" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE")

        if [[ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_ENABLE" = "yes" ]]; then
            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE=$(ask_yes_no "Enable reliable disk buffering (recommended: no for normal buffering)?" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE")

            if [[ "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_RELIABLE" = "yes" ]]; then
                SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE=$(read_numeric "Worker memory buffer size in bytes (for reliable buffering)" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_MEMBUFSIZE")
            fi

            SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE=$(read_numeric "Disk buffer size in bytes (default 50GB per worker)" "$SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE")
        fi
    fi

    # Timezone Configuration
    echo ""
    printf "${GREEN}=== Timezone Configuration ===${NC}\n"
    echo "SC4S can force a default timezone for events that lack a timezone offset."
    echo "This is useful for legacy sources that send timestamps without timezone info."
    echo ""

    CONFIGURE_TIMEZONE=$(ask_yes_no "Configure a default timezone?" "no")
    if [[ "$CONFIGURE_TIMEZONE" = "yes" ]]; then
        echo ""
        echo "Enter a timezone in Region/City format."
        echo "Examples: America/New_York, Europe/London, Asia/Tokyo, US/Eastern"
        echo ""
        while true; do
            read -p "Timezone: " SC4S_DEFAULT_TIMEZONE
            if [[ -z "$SC4S_DEFAULT_TIMEZONE" ]]; then
                printf "${RED}Timezone cannot be empty.${NC}\n"
            elif [[ "$SC4S_DEFAULT_TIMEZONE" =~ ^[A-Za-z_]+/[A-Za-z_]+(/[A-Za-z_]+)?$ ]]; then
                break
            else
                printf "${RED}Invalid format. Use Region/City (e.g., America/New_York).${NC}\n"
            fi
        done
    fi

elif [[ "$mode_choice" = "2" ]]; then
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
    printf "${GREEN}=== Expected Events Per Second ===${NC}\n"
    printf "${GREEN}For larger traffic volume, configuration will be adjusted to optimize performance.${NC}\n"
    EXPECTED_EPS=$(read_numeric "Expected events per second (EPS)" "10000")

    echo ""
    echo "Select primary protocol:"
    echo "1) UDP (faster, best for high volume)"
    echo "2) TCP (reliable, guaranteed delivery)"
    echo "3) Both UDP and TCP"
    echo ""
    read -p "Select protocol [1]: " proto_choice
    proto_choice=${proto_choice:-1}

    case "$proto_choice" in
        1) PROTOCOL="udp";;
        2) PROTOCOL="tcp";;
        3) PROTOCOL="both";;
        *) PROTOCOL="udp";;
    esac

    # Apply hardware-based configuration
    apply_hardware_config "$HARDWARE" "$PROTOCOL" "$EXPECTED_EPS"

    # Splunk configuration
    echo ""
    printf "${GREEN}=== Splunk Configuration ===${NC}\n"
    read_hec_url
    read_hec_token
    TLS_VERIFY=$(ask_yes_no "Verify SSL/TLS certificates?" "yes")

else
    printf "${RED}Invalid mode selection. Please run the tool again.${NC}\n"
    exit 1
fi

# Output file
echo ""
read -p "Output filename [$OUTPUT_FILE]: " input_output
OUTPUT_FILE=${input_output:-$OUTPUT_FILE}

while [[ -f "$OUTPUT_FILE" ]]; do
    printf "${YELLOW}Warning: '$OUTPUT_FILE' already exists.${NC}\n"
    OVERWRITE=$(ask_yes_no "Overwrite it?" "no")
    if [[ "$OVERWRITE" = "yes" ]]; then
        break
    fi
    read -p "Enter a different filename: " OUTPUT_FILE
    if [[ -z "$OUTPUT_FILE" ]]; then
        printf "${RED}No filename provided. Aborting.${NC}\n"
        exit 1
    fi
done

# Build configuration through the same renderer used by non-interactive mode.
build_config

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
if [[ "$CONFIRM" != "yes" ]]; then
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
if [[ "$SC4S_SOURCE_UDP_SO_RCVBUFF" -gt 0 || "$SC4S_SOURCE_TCP_SO_RCVBUFF" -gt 0 ]]; then
    echo ""
    printf "${YELLOW}Note: You need to adjust your system's receiving buffer to match the configured values.${NC}\n"
    echo "Add the following to /etc/sysctl.conf:"
    echo ""
    RCVBUFF_MAX=0
    if [[ "$SC4S_SOURCE_UDP_SO_RCVBUFF" -gt "$RCVBUFF_MAX" ]]; then
        RCVBUFF_MAX=$SC4S_SOURCE_UDP_SO_RCVBUFF
    fi
    if [[ "$SC4S_SOURCE_TCP_SO_RCVBUFF" -gt "$RCVBUFF_MAX" ]]; then
        RCVBUFF_MAX=$SC4S_SOURCE_TCP_SO_RCVBUFF
    fi
    if [[ "$RCVBUFF_MAX" -gt 0 ]]; then
        printf "${GREEN}  net.core.rmem_default = %s${NC}\n" "$RCVBUFF_MAX"
        printf "${GREEN}  net.core.rmem_max = %s${NC}\n" "$RCVBUFF_MAX"
    fi
    echo ""
    echo "Then apply with:  sudo sysctl -p"
    echo ""
    echo "Documentation: https://splunk.github.io/splunk-connect-for-syslog/main/architecture/fine-tuning/#tune-the-receiving-buffer"
fi


if [[ "$SC4S_ENABLE_EBPF" = "yes" ]]; then
echo ""
printf "${YELLOW}Note: Enabling eBPF may require additional system permissions.${NC}\n"
echo "Ensure that your system supports eBPF and that the necessary capabilities are granted to the SC4S process or container. Read more here: "
echo "https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#about-ebpf"
fi


if [[ "$TLS_VERIFY" = "no" ]]; then
    echo ""
    printf "${YELLOW}Warning: TLS certificate verification is DISABLED (SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no).${NC}\n"
    echo "SC4S will not validate the Splunk HEC server's certificate, which exposes the connection"
    echo "to attacks. This setting is intended for development/testing with self-signed"
    echo "certificates. For production, use a certificate signed by a trusted CA and re-enable TLS"
    echo "verification."
    echo "Documentation: https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#configure-your-syslog-source-tls-certificate"
fi

if [[ "$SPLUNK_URL" =~ ^http:// ]]; then
    echo ""
    printf "${YELLOW}Warning: Provided Splunk HEC URL uses plaintext HTTP instead of HTTPS.${NC}\n"
    echo "Traffic to '$SPLUNK_URL' will not be encrypted. The Splunk HEC token and event data"
    echo "(which may contain sensitive log content) will be transmitted in clear text and can be"
    echo "intercepted on the network. Use an https:// HEC endpoint for any non-isolated environment."
fi

#!/bin/bash

#################################################
# PCAP Rewrite and Replay Script
# Purpose: Modify PCAP file using Scapy and replay with tcpreplay
#################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default Python script location (same directory as bash script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/pcap_rewrite.py"

# Function to display usage
usage() {
    echo -e "${YELLOW}Usage:${NC} $0 [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  -i <input.pcap>         Input PCAP file path"
    echo "  -o <output.pcap>        Output PCAP file path"
    echo "  -n <interface>          Network interface for replay (e.g., eth0)"
    echo ""
    echo "Optional Rewrites:"
    echo "  -d <dest_ip>            Destination IP address to rewrite"
    echo "  -P <dest_port>          Destination port to rewrite"
    echo "  -m <dest_mac>           Destination MAC address (format: aa:bb:cc:dd:ee:ff)"
    echo "  -s <src_ip>             Source IP address to rewrite"
    echo "  -p <src_port>           Source port to rewrite"
    echo "  -M <src_mac>            Source MAC address (format: aa:bb:cc:dd:ee:ff)"
    echo ""
    echo "Python Environment:"
    echo "  -e <venv_path>          Path to Python virtual environment (optional)"
    echo "                          If not specified, will try to detect active venv"
    echo ""
    echo "Replay Options:"
    echo "  -r <replay_speed>       Replay speed multiplier (default: 1)"
    echo "  -l <loop_count>         Number of times to loop replay (default: 1, 0 = infinite)"
    echo "  -R                      Skip replay (only generate modified PCAP)"
    echo ""
    echo "Other Options:"
    echo "  -v                      Verbose mode (show packet samples)"
    echo "  -I                      Show input PCAP info only (no modification/replay)"
    echo "  -y                      Auto-confirm replay (skip confirmation prompt)"
    echo "  -h                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Use active virtual environment"
    echo "  $0 -i input.pcap -o output.pcap -n eth0 -d 192.168.1.100"
    echo ""
    echo "  # Specify virtual environment path"
    echo "  $0 -e /path/to/venv -i input.pcap -o output.pcap -n eth0 -d 192.168.1.100"
    echo ""
    echo "  # Use system Python (no venv)"
    echo "  $0 -e none -i input.pcap -o output.pcap -n eth0 -d 192.168.1.100"
    exit 1
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect Python command and virtual environment
detect_python_env() {
    local venv_path="$1"

    # If venv_path is "none", use system Python
    if [[ "$venv_path" == "none" ]]; then
        if command_exists "python3"; then
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
        elif command_exists "python"; then
            PYTHON_CMD="python"
            PIP_CMD="pip"
        else
            echo -e "${RED}Error:${NC} Python not found"
            exit 1
        fi
        echo -e "${YELLOW}Using system Python:${NC} $PYTHON_CMD"
        return 0
    fi

    # If venv_path is specified, use it
    if [[ -n "$venv_path" ]]; then
        if [[ ! -d "$venv_path" ]]; then
            echo -e "${RED}Error:${NC} Virtual environment not found at: $venv_path"
            exit 1
        fi

        # Check for Python in venv
        if [[ -f "$venv_path/bin/python" ]]; then
            PYTHON_CMD="$venv_path/bin/python"
            PIP_CMD="$venv_path/bin/pip"
            echo -e "${GREEN}Using virtual environment:${NC} $venv_path"
            return 0
        elif [[ -f "$venv_path/Scripts/python.exe" ]]; then
            # Windows venv
            PYTHON_CMD="$venv_path/Scripts/python.exe"
            PIP_CMD="$venv_path/Scripts/pip.exe"
            echo -e "${GREEN}Using virtual environment:${NC} $venv_path"
            return 0
        else
            echo -e "${RED}Error:${NC} Python not found in virtual environment: $venv_path"
            exit 1
        fi
    fi

    # Try to detect active virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        venv_path="$VIRTUAL_ENV"
        if [[ -f "$venv_path/bin/python" ]]; then
            PYTHON_CMD="$venv_path/bin/python"
            PIP_CMD="$venv_path/bin/pip"
            echo -e "${GREEN}Detected active virtual environment:${NC} $venv_path"
            return 0
        fi
    fi

    # Check if we're in a Poetry environment
    if command_exists "poetry" && [[ -f "pyproject.toml" ]]; then
        PYTHON_CMD="poetry run python"
        PIP_CMD="poetry run pip"
        echo -e "${GREEN}Detected Poetry environment${NC}"
        return 0
    fi

    # Check if we're in a Conda environment
    if [[ -n "$CONDA_DEFAULT_ENV" ]] && command_exists "conda"; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
        echo -e "${GREEN}Detected Conda environment:${NC} $CONDA_DEFAULT_ENV"
        return 0
    fi

    # Check for pipenv
    if command_exists "pipenv" && [[ -f "Pipfile" ]]; then
        PYTHON_CMD="pipenv run python"
        PIP_CMD="pipenv run pip"
        echo -e "${GREEN}Detected Pipenv environment${NC}"
        return 0
    fi

    # Fall back to system Python
    if command_exists "python3"; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command_exists "python"; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        echo -e "${RED}Error:${NC} Python not found"
        exit 1
    fi

    echo -e "${YELLOW}No virtual environment detected. Using system Python:${NC} $PYTHON_CMD"
    echo -e "${YELLOW}Tip:${NC} Activate your venv first or use -e option to specify venv path"
}

# Function to check Python script exists
check_python_script() {
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        echo -e "${RED}Error:${NC} Python script not found at: $PYTHON_SCRIPT"
        echo "Please ensure pcap_rewrite.py is in the same directory as this script"
        exit 1
    fi
}

# Function to check if Scapy is installed
check_scapy() {
    if $PYTHON_CMD -c "import scapy.all" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to install Scapy
install_scapy() {
    echo -e "${YELLOW}Scapy not found in current Python environment${NC}"
    echo -e "${YELLOW}Installing Scapy...${NC}"

    $PIP_CMD install scapy

    if [[ $? -ne 0 ]]; then
        echo -e "${RED}Error:${NC} Failed to install Scapy"
        echo ""
        echo "Please install manually:"
        echo "  $PIP_CMD install scapy"
        exit 1
    fi

    # Verify installation
    if ! check_scapy; then
        echo -e "${RED}Error:${NC} Scapy installation verification failed"
        exit 1
    fi

    echo -e "${GREEN}✓ Scapy installed successfully${NC}"
}

# Function to show Python environment info
show_python_info() {
    echo -e "${BLUE}Python Environment Information:${NC}"
    echo "  Python command: $PYTHON_CMD"

    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo "  Python version: $PYTHON_VERSION"

    # Get Python path
    PYTHON_PATH=$($PYTHON_CMD -c "import sys; print(sys.executable)" 2>/dev/null)
    echo "  Python path: $PYTHON_PATH"

    # Check if in venv
    IN_VENV=$($PYTHON_CMD -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))" 2>/dev/null)
    if [[ "$IN_VENV" == "True" ]]; then
        echo -e "  Virtual env: ${GREEN}Yes${NC}"
    else
        echo -e "  Virtual env: ${YELLOW}No (using system Python)${NC}"
    fi

    # Check Scapy version
    SCAPY_VERSION=$($PYTHON_CMD -c "import scapy; print(scapy.__version__)" 2>/dev/null)
    if [[ -n "$SCAPY_VERSION" ]]; then
        echo "  Scapy version: $SCAPY_VERSION"
    fi
    echo ""
}

# Initialize variables
INPUT_PCAP=""
OUTPUT_PCAP=""
INTERFACE=""
DEST_IP=""
DEST_PORT=""
DEST_MAC=""
SRC_IP=""
SRC_PORT=""
SRC_MAC=""
VENV_PATH=""
REPLAY_SPEED="1"
LOOP_COUNT="1"
SKIP_REPLAY=0
VERBOSE=0
INFO_ONLY=0
AUTO_CONFIRM=0
PYTHON_CMD=""
PIP_CMD=""

# Parse command line arguments
while getopts "i:o:n:d:P:m:s:p:M:e:r:l:RvIyh" opt; do
    case $opt in
        i) INPUT_PCAP="$OPTARG" ;;
        o) OUTPUT_PCAP="$OPTARG" ;;
        n) INTERFACE="$OPTARG" ;;
        d) DEST_IP="$OPTARG" ;;
        P) DEST_PORT="$OPTARG" ;;
        m) DEST_MAC="$OPTARG" ;;
        s) SRC_IP="$OPTARG" ;;
        p) SRC_PORT="$OPTARG" ;;
        M) SRC_MAC="$OPTARG" ;;
        e) VENV_PATH="$OPTARG" ;;
        r) REPLAY_SPEED="$OPTARG" ;;
        l) LOOP_COUNT="$OPTARG" ;;
        R) SKIP_REPLAY=1 ;;
        v) VERBOSE=1 ;;
        I) INFO_ONLY=1 ;;
        y) AUTO_CONFIRM=1 ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Validate required parameters
if [[ -z "$INPUT_PCAP" ]]; then
    echo -e "${RED}Error:${NC} Input PCAP file (-i) is required"
    usage
fi

if [[ $INFO_ONLY -eq 0 ]] && [[ -z "$OUTPUT_PCAP" ]]; then
    echo -e "${RED}Error:${NC} Output PCAP file (-o) is required"
    usage
fi

if [[ -z "$INTERFACE" ]]; then
    echo -e "${RED}Error:${NC} Network interface (-n) is required"
    usage
fi

# Banner
echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        PCAP Rewrite and Replay Tool (Scapy + tcpreplay)  ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect and setup Python environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
detect_python_env "$VENV_PATH"
echo ""

# Show Python info if verbose
if [[ $VERBOSE -eq 1 ]]; then
    show_python_info
fi

# Check if required tools are installed
echo -e "${YELLOW}Checking required tools...${NC}"

# Check for Python script
check_python_script
echo -e "${GREEN}✓ pcap_rewrite.py found${NC}"

# Check for Scapy
if check_scapy; then
    echo -e "${GREEN}✓ scapy installed${NC}"
else
    install_scapy
fi

# Check for tcpreplay (only if not skipping replay)
if [[ $SKIP_REPLAY -eq 0 ]] && [[ $INFO_ONLY -eq 0 ]]; then
    if ! command_exists "tcpreplay"; then
        echo -e "${RED}Error:${NC} tcpreplay is not installed"
        echo "Ubuntu/Debian: sudo apt-get install tcpreplay"
        echo "CentOS/RHEL: sudo yum install tcpreplay"
        exit 1
    fi
    echo -e "${GREEN}✓ tcpreplay installed${NC}"
fi

echo ""

# Validate input file exists
if [[ ! -f "$INPUT_PCAP" ]]; then
    echo -e "${RED}Error:${NC} Input file '$INPUT_PCAP' not found"
    exit 1
fi

# If info only mode, just show info and exit
if [[ $INFO_ONLY -eq 1 ]]; then
    echo -e "${YELLOW}Showing PCAP information...${NC}\n"
    $PYTHON_CMD "$PYTHON_SCRIPT" -i "$INPUT_PCAP" --info
    exit 0
fi

# Build Python command arguments
PYTHON_ARGS="-i \"$INPUT_PCAP\" -o \"$OUTPUT_PCAP\""

if [[ -n "$SRC_IP" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -s $SRC_IP"
fi

if [[ -n "$DEST_IP" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -d $DEST_IP"
fi

if [[ -n "$SRC_PORT" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -p $SRC_PORT"
fi

if [[ -n "$DEST_PORT" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -P $DEST_PORT"
fi

if [[ -n "$SRC_MAC" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -M $SRC_MAC"
fi

if [[ -n "$DEST_MAC" ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -m $DEST_MAC"
fi

if [[ $VERBOSE -eq 1 ]]; then
    PYTHON_ARGS="$PYTHON_ARGS -v"
fi

# Execute the Python script
echo -e "${GREEN}Starting PCAP modification with Scapy...${NC}\n"

if [[ $VERBOSE -eq 1 ]]; then
    echo -e "${BLUE}Executing:${NC} $PYTHON_CMD \"$PYTHON_SCRIPT\" $PYTHON_ARGS"
    echo ""
fi

eval "$PYTHON_CMD \"$PYTHON_SCRIPT\" $PYTHON_ARGS"

if [[ $? -ne 0 ]]; then
    echo -e "\n${RED}Error:${NC} PCAP modification failed"
    exit 1
fi

echo -e "\n${GREEN}✓ PCAP modification completed${NC}\n"

# Display file info
echo -e "${YELLOW}PCAP File Information:${NC}"
echo "  Input file:  $INPUT_PCAP"
echo "  Output file: $OUTPUT_PCAP"

if command_exists "ls"; then
    INPUT_SIZE=$(ls -lh "$INPUT_PCAP" 2>/dev/null | awk '{print $5}')
    OUTPUT_SIZE=$(ls -lh "$OUTPUT_PCAP" 2>/dev/null | awk '{print $5}')
    echo "  Input size:  $INPUT_SIZE"
    echo "  Output size: $OUTPUT_SIZE"
fi

if command_exists "capinfos"; then
    echo ""
    capinfos "$OUTPUT_PCAP" 2>/dev/null | grep -E "Number of packets|File size|Capture duration" || true
fi
echo ""

# Verify changes with tcpdump if available
if command_exists "tcpdump"; then
    echo -e "${YELLOW}Sample packets from modified PCAP:${NC}"
    tcpdump -n -r "$OUTPUT_PCAP" -c 3 2>/dev/null
    echo ""
fi

# Replay the PCAP (if not skipped)
if [[ $SKIP_REPLAY -eq 1 ]]; then
    echo -e "${GREEN}Replay skipped as requested.${NC}"
    echo "Modified PCAP saved at: $OUTPUT_PCAP"
    exit 0
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    REPLAY CONFIGURATION                   ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if interface exists
if ! ip link show "$INTERFACE" &>/dev/null; then
    echo -e "${RED}Error:${NC} Interface $INTERFACE not found"
    echo ""
    echo "Available interfaces:"
    ip link show | grep -E "^[0-9]+:" | cut -d: -f2 | sed 's/^ /  - /'
    exit 1
fi

# Check if interface is up
INTERFACE_STATE=$(ip link show "$INTERFACE" | grep -o "state [A-Z]*" | awk '{print $2}')
echo -e "${YELLOW}Interface Status:${NC}"
echo "  Interface: $INTERFACE"
echo "  State: $INTERFACE_STATE"

if [[ "$INTERFACE_STATE" != "UP" ]]; then
    echo -e "  ${YELLOW}Warning: Interface is not UP${NC}"
    read -p "  Do you want to bring it up? (yes/no): " bring_up
    if [[ "$bring_up" == "yes" ]]; then
        sudo ip link set "$INTERFACE" up
        sleep 1
        echo -e "  ${GREEN}✓ Interface brought up${NC}"
    fi
fi
echo ""

echo -e "${YELLOW}Replay Settings:${NC}"
echo "  PCAP file: $OUTPUT_PCAP"
echo "  Interface: $INTERFACE"
echo "  Speed multiplier: ${REPLAY_SPEED}x"
echo "  Loop count: $LOOP_COUNT"

if [[ "$LOOP_COUNT" == "0" ]]; then
    echo -e "  ${YELLOW}(Infinite loop - press Ctrl+C to stop)${NC}"
fi
echo ""

# Confirmation prompt
if [[ $AUTO_CONFIRM -eq 0 ]]; then
    echo -e "${RED}⚠ WARNING: This will send actual network traffic! ⚠${NC}"
    read -p "Continue with replay? (yes/no): " confirm

    if [[ "$confirm" != "yes" ]]; then
        echo "Replay cancelled. Modified PCAP saved at: $OUTPUT_PCAP"
        exit 0
    fi
fi

echo ""
echo -e "${GREEN}Starting replay...${NC}"
echo ""

# Add after "Starting replay..." and before eval $TCPREPLAY_CMD

# Pre-flight checks
echo -e "${YELLOW}Pre-flight checks:${NC}"

# Check packet count
PACKET_COUNT=$(tcpdump -n -r "$OUTPUT_PCAP" 2>/dev/null | wc -l)
echo "  Packets in PCAP: $PACKET_COUNT"

if [[ $PACKET_COUNT -eq 0 ]]; then
    echo -e "${RED}Error: No packets in PCAP file!${NC}"
    exit 1
fi

# Show what will be sent
echo "  Sample packet destinations:"
tcpdump -n -r "$OUTPUT_PCAP" -c 3 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -3

# Check interface is actually up
INTERFACE_STATE=$(ip link show "$INTERFACE" | grep -o "state [A-Z]*" | awk '{print $2}')
echo "  Interface state: $INTERFACE_STATE"

if [[ "$INTERFACE_STATE" != "UP" ]]; then
    echo -e "${RED}Error: Interface is not UP!${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}Tip: Run this in another terminal to see packets:${NC}"
echo "  sudo tcpdump -i $INTERFACE -n -v"
echo "  or"
echo "  sudo tcpdump -i any -n 'host <destination_ip>'"
echo ""
read -p "Press Enter when tcpdump is ready..."

# Use more verbose tcpreplay options
TCPREPLAY_CMD="sudo tcpreplay --intf1=\"$INTERFACE\" --multiplier=\"$REPLAY_SPEED\" --stats=10 --verbose"

# Build tcpreplay command
TCPREPLAY_CMD="sudo tcpreplay --intf1=\"$INTERFACE\" --multiplier=\"$REPLAY_SPEED\" --stats=1"

TCPREPLAY_CMD="$TCPREPLAY_CMD \"$OUTPUT_PCAP\""

# Execute replay
eval $TCPREPLAY_CMD

if [[ $? -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✓ Replay completed successfully${NC}"
else
    echo ""
    echo -e "${RED}Error:${NC} Replay failed"
    echo -e "${YELLOW}Troubleshooting tips:${NC}"
    echo "  1. Check interface status: ip link show $INTERFACE"
    echo "  2. Verify you have root/sudo privileges"
    echo "  3. Check if interface supports packet injection"
    echo "  4. Try with --mbps or --pps options for rate limiting"
    exit 1
fi

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    OPERATION COMPLETE                     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}All operations completed successfully!${NC}"
echo "Modified PCAP file: $OUTPUT_PCAP"
echo ""
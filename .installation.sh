#!/bin/bash

# Detect OS
os_release=$(grep ^ID= /etc/os-release | cut -d= -f2 | tr -d '"')
os_version=$(rpm -E %{rhel} 2>/dev/null || lsb_release -sr 2>/dev/null)

# Check if the OS is Rocky 8.5 or Ubuntu 22.04
if [[ ("$os_release" == "rocky" && "$os_version" -eq 8) || ("$os_release" == "ubuntu" && "$os_version" == "22.04") ]]; then
    echo "Detected OS: $os_release $os_version"
else
    echo "Unsupported OS. This script supports only Rocky Linux 8.5 and Ubuntu 22.04."
    exit 1
fi

# Function to install SC4S using podman
install_sc4s() {
    echo "Installing SC4S..."

    # Install podman if missing
    if ! command -v podman &>/dev/null; then
        echo "Installing podman..."
        if [[ "$os_release" == "rocky" ]]; then
            sudo dnf install -y podman
        else
            sudo apt update
            sudo apt install -y podman
        fi
    fi

    # Enable IPv4 forwarding if not enabled
    if [[ "$(sysctl -n net.ipv4.ip_forward)" -ne 1 ]]; then
        echo "Enabling IPv4 forwarding..."
        echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-sysctl.conf
        sudo sysctl --system
    fi

    # Get user inputs
    read -p "Enter your Splunk instance URL (e.g., https://splunk_ip:8088 or https://splunkcloudhecurl): " splunk_url
    read -p "Enter your Splunk HEC token: " splunk_token
    read -p "Enter the SC4S image tag (e.g., latest, 3.0.0): " sc4s_tag

# Create systemd service for SC4S using podman
    echo "Setting up SC4S service..."
cat <<EOF | sudo tee /lib/systemd/system/sc4s.service
[Unit]
Description=SC4S Container
Wants=NetworkManager.service network-online.target
After=NetworkManager.service network-online.target

[Install]
WantedBy=multi-user.target

[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container3:$sc4s_tag"
Environment="SC4S_PERSIST_MOUNT=splunk-sc4s-var:/var/lib/syslog-ng"
Environment="SC4S_LOCAL_MOUNT=/opt/sc4s/local:/etc/syslog-ng/conf.d/local:z"
Environment="SC4S_ARCHIVE_MOUNT=/opt/sc4s/archive:/var/lib/syslog-ng/archive:z"
Environment="SC4S_TLS_MOUNT=/opt/sc4s/tls:/etc/syslog-ng/tls:z"
TimeoutStartSec=0

ExecStartPre=/usr/bin/podman pull \$SC4S_IMAGE
ExecStartPre=/usr/bin/bash -c "/usr/bin/systemctl set-environment SC4SHOST=\$(hostname -s)"
ExecStart=/usr/bin/podman run \
        -e "SC4S_CONTAINER_HOST=\${SC4SHOST}" \
        -v "\$SC4S_PERSIST_MOUNT" \
        -v "\$SC4S_LOCAL_MOUNT" \
        -v "\$SC4S_ARCHIVE_MOUNT" \
        -v "\$SC4S_TLS_MOUNT" \
        --env-file=/opt/sc4s/env_file \
        --health-cmd="/healthcheck.sh" \
        --health-interval=10s --health-retries=6 --health-timeout=6s \
        --network host \
        --name SC4S \
        --rm \$SC4S_IMAGE

Restart=on-abnormal
EOF

# Create podman volume
sudo podman volume create splunk-sc4s-var

# Create  directories
sudo mkdir -p /opt/sc4s/local /opt/sc4s/archive /opt/sc4s/tls

# Step 4: Create environment file
cat <<EOF | sudo tee /opt/sc4s/env_file
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$splunk_url
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=$splunk_token
# Uncomment the following line if using untrusted SSL certificates
SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no
EOF


    # Enable and start SC4S service
    sudo systemctl daemon-reload
    sudo systemctl enable sc4s
    sudo systemctl start sc4s
    sleep 10
    sudo systemctl stop sc4s
    sleep 10 
    sudo systemctl start sc4s

    echo "SC4S installation complete!"
}

# Function to configure Splunk indexes and HEC token with configuration files
install_splunk_indexes() {
    echo "Setting up Splunk indexes and HEC token..."

    SPLUNK_HOME="/opt/splunk"
    APP_NAME="sc4s_indexes"
    APP_DIR="$SPLUNK_HOME/etc/apps/$APP_NAME"
    HEC_APP_DIR="$SPLUNK_HOME/etc/apps/splunk_httpinput"

    # Generate a UUID for the HEC token
    HEC_TOKEN=$(uuidgen)
    echo "Generated HEC Token: $HEC_TOKEN"

    # Ensure Splunk is running
    if ! pgrep -f splunkd > /dev/null; then
        echo "Starting Splunk..."
        sudo $SPLUNK_HOME/bin/splunk start --accept-license --no-prompt
    fi

    # Create app directory structure
    sudo mkdir -p "$APP_DIR/local"
    sudo mkdir -p "$APP_DIR/metadata"
    sudo mkdir -p "$APP_DIR/default"
    sudo mkdir -p "$HEC_APP_DIR/local"

    # Create metadata file
    cat <<EOF | sudo tee "$APP_DIR/metadata/default.meta"
[]
access = read : [ * ], write : [ admin ]
export = system
EOF

    # Create indexes.conf file
    cat <<EOF | sudo tee "$APP_DIR/local/indexes.conf"
##
## SPDX-FileCopyrightText: 2021 Splunk, Inc. <sales@splunk.com>
## SPDX-License-Identifier: LicenseRef-Splunk-8-2021
##
##

[syslogng_metrics]
datatype=metric
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[comms]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[email]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[epav]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[fireeye]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[epintel]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[em_logs]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[em_meta]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[_metrics]
datatype=metric
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[syslogng_fallback]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[infraops]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[osnix]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[oswin]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[oswinsec]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netauth]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netdlp]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netdns]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netfw]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netids]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netipam]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netlb]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netops]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netmetrics]
datatype=metric
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netproxy]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[netwaf]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[print]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[gitops]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb

[lastchance]
repFactor = auto
journalCompression = zstd
homePath   = \$SPLUNK_DB/\$_index_name/db
coldPath   = \$SPLUNK_DB/\$_index_name/coldb
thawedPath = \$SPLUNK_DB/\$_index_name/thaweddb
EOF

    # update local inputs.conf for HEC
    cat <<EOF | sudo tee "$HEC_APP_DIR/local/inputs.conf"
[http]
disabled=0
port=8088
enableSSL=1
dedicatedIoThreads=2
maxThreads = 0
maxSockets = 0
useDeploymentServer=0
rollingRestartReturnServerBusy=true
# ssl settings are similar to mgmt server
sslVersions=*,-ssl2
allowSslCompression=true
allowSslRenegotiation=true
ackIdleCleanup=true
EOF

    # Create local inputs.conf for HTTP Event Collector
    cat <<EOF | sudo tee "$APP_DIR/local/inputs.conf"
[http://test]
disabled = 0
token = $HEC_TOKEN
useACK = 0
EOF

    # Set permissions
    sudo chown -R splunk:splunk "$APP_DIR"
    sudo chmod -R 755 "$APP_DIR"

    # Restart Splunk to apply changes
    sudo $SPLUNK_HOME/bin/splunk restart

    echo "Splunk indexes and HEC token setup completed!"
    echo "Your generated HEC Token is: $HEC_TOKEN"
    echo "Your HEC endpoint is https://localhost:8088"
}

# Check user input and execute the appropriate function
if [[ "$1" == "sc4s" ]]; then
    install_sc4s
elif [[ "$1" == "splunk" ]]; then
    install_splunk_indexes
else
    echo "Usage: $0 {sc4s|splunk}"
    exit 1
fi

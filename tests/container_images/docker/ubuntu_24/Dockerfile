FROM ubuntu:24.04

# Use bash with pipefail for robust scripting
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set environment variables for non-interactive apt and Poetry
ENV DEBIAN_FRONTEND=noninteractive
# Poetry installer will put its binaries here, ensure it's in PATH
ENV PATH="/root/.local/bin:$PATH"

# Define ARGs for versions (important for cache invalidation and clarity)
ARG ANSIBLE_VERSION="6.1.0" # Or specify ansible-core version
ARG ANSIBLE_CORE_VERSION="2.13.13" # Based on your previous output
ARG POETRY_INSTALLER_VERSION="1.5.1" # For the global poetry install
ARG MICROK8S_CHANNEL="1.28/stable" # Specify MicroK8s channel

# 1. Install common system dependencies first
# This helps consolidate apt updates and reduce image layers
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    curl \
    gnupg \
    lsb-release \
    build-essential \
    parallel \
    sshpass \
    git \
    jq \
    # For Docker installation
    ca-certificates \
    # For MicroK8s
    snapd \
    systemd \
    systemd-udev \
    dbus \
    # Clean up apt cache to keep image small
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python versions
# Use deadsnakes PPA for older Python versions on newer Ubuntu
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends \
    python3.7 python3.7-venv python3.7-dev \
    python3.9 python3.9-venv python3.9-dev \
    python3.12 python3.12-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Ensure python3 points to 3.12 (default on Ubuntu 24.04) and pip3 to its pip
# This makes 'python3' and 'pip3' commands consistent
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 100 \
    && update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.12 100

# 4. Prepare python venv and install tools orca and cloudctl
# Using a single RUN layer for efficiency and to manage secrets
RUN --mount=type=secret,id=pipconf,dst=/root/.pip/pip.conf \
    # Create virtual environments in a common location
    python3.12 -m venv /opt/.venv3.12 && \
    python3.9 -m venv /opt/.venv3.9 && \
    python3.7 -m venv /opt/.venv3.7 && \
    \
    # Install Poetry globally using its installer (for default Python 3.12)
    # This ensures 'poetry' command is available without venv activation
    curl -sSL https://install.python-poetry.org | python3.12 - --version "${POETRY_INSTALLER_VERSION}"

# 5. Install Ansible globally for the default python3 (3.12)
RUN /opt/.venv3.9/pip3 install ansible=="${ANSIBLE_VERSION}" ansible-core=="${ANSIBLE_CORE_VERSION}" docker pywinrm

# 6. Install Docker
# Add Docker's official GPG key
RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg

# Add the Docker repository to Apt sources
RUN echo \
  "deb [arch=\"$(dpkg --print-architecture)\" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  \"$(. /etc/os-release && echo \"$VERSION_CODENAME\")\" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Add a 'docker' group to prevent permission issues (though in CI, often run as root)
RUN groupadd docker || true

# 7. Install Podman (Available via apt on Ubuntu)
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    podman \
    && rm -rf /var/lib/apt/lists/*

# Clean up any temporary files or caches created during the build to reduce image size
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set default command or entrypoint if desired for interactive use
# ENTRYPOINT ["/bin/bash"]
# CMD ["/bin/bash"]

RUN systemctl mask systemd-logind.service \
                   systemd-udevd.service \
                   systemd-journald.service \
                   systemd-resolved.service \
                   networkd.service \
                   getty@.service \
                   graphical.target \
                   multi-user.target \
                   plymouth-quit-wait.service \
                   plymouth-start.service \
                   systemd-update-utmp-runlevel.service \
                   systemd-update-utmp.service \
                   systemd-vconsole-setup.service \
                   console-getty.service || true

CMD ["/usr/sbin/init"]
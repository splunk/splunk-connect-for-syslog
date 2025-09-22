# syntax=docker/dockerfile:1.4
FROM redhat/ubi9

# Use bash with pipefail for robust scripting
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set environment variables for Poetry
ENV PATH="/root/.local/bin:$PATH"

# Define ARGs for versions (important for cache invalidation and clarity)
ARG ANSIBLE_VERSION="6.1.0"
ARG ANSIBLE_CORE_VERSION="2.13.13"
ARG POETRY_INSTALLER_VERSION="1.5.1"
ARG KUSTOMIZE_VER=5.3.0

# 1. Install common system dependencies first
RUN dnf install -y --allowerasing https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm && \
    dnf install -y --allowerasing \
    dnf-utils \
    curl \
    gnupg2 \
    make \
    gcc \
    parallel \
    sshpass \
    git \
    jq \
    ca-certificates \
    systemd \
    systemd-udev \
    dbus \
    && dnf clean all

# 2. Install Python versions
# UBI9 default python3 is 3.9 is available via modules.
# Python 3.7 and 3.12 are not directly available in default repos for RHEL9/UBI9.
RUN dnf install -y --allowerasing \
    python3.9 \
    python3.9-devel \
    python3.9-pip \
    && dnf clean all

# 4. Prepare python venv and install tools
RUN --mount=type=secret,id=pipconf,dst=/root/.pip/pip.conf \
    # Create virtual environments in a common location
    python3.9 -m venv /opt/.venv3.9 && \
    curl -sSL https://install.python-poetry.org | /opt/.venv3.9/bin/python - --version "${POETRY_INSTALLER_VERSION}"

# 5. Install Ansible into the /opt/.venv3.9 virtual environment
RUN /opt/.venv3.9/bin/pip install --no-cache-dir \
    ansible=="${ANSIBLE_VERSION}" \
    ansible-core=="${ANSIBLE_CORE_VERSION}" \
    docker \
    pywinrm \
    requests

# Add the /opt/.venv3.9/bin to PATH so 'ansible-playbook' etc. are found
ENV PATH="/opt/.venv3.9/bin:$PATH"

# 6. Install Docker
# Add Docker's official repository for CentOS/RHEL
RUN dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && \
    dnf install -y --allowerasing \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    && dnf clean all

# Add a 'docker' group (though in CI, often run as root)
RUN groupadd docker || true

# 7. Install Podman (usually pre-installed or easily available)
RUN dnf install -y --allowerasing podman && \
    dnf clean all

# Clean up any temporary files or caches created during the build to reduce image size
RUN dnf autoremove -y && \
    dnf clean all && \
    rm -rf /tmp/* /var/tmp/*


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

ENTRYPOINT ["/usr/sbin/init"]
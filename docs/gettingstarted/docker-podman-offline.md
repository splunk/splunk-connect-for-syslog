# Install a container while offline

You can stage SC4S by downloading the image so that it can be loaded on a
host machine, for example on an airgapped system, without internet connectivity.

1. Download the container image ``oci_container.tgz`` from our [Github Page](https://github.com/splunk/splunk-connect-for-syslog/releases). The following example downloads v3.23.1, replace the URL with the latest release or pre-release version as desired:

```
sudo wget https://github.com/splunk/splunk-connect-for-syslog/releases/download/v3.23.1/oci_container.tar.gz
```

2. Distribute the container to the airgapped host machine using your preferred file transfer utility.
3. Execute the following command, using Docker or Podman:

```
<podman or docker> load < oci_container.tar.gz
```

4. Make a note of the container ID for the resulting load:

```
Loaded image: ghcr.io/splunk/splunk-connect-for-syslog/container3:3.23.1
```

5. Use the container ID to create a local label:
```
<podman or docker> tag ghcr.io/splunk/splunk-connect-for-syslog/container3:3.23.1 sc4slocal:latest
```

6. Use the local label `sc4slocal:latest` in the relevant unit or YAML file to launch SC4S by setting the `SC4S_IMAGE` environment variable in the unit file, or the relevant `image:` tag if you are using Docker Compose/Swarm. This label will cause the runtime to select the locally loaded image, and will not attempt to obtain the container image from the internet.

```
Environment="SC4S_IMAGE=sc4slocal:latest"
```
7. Remove the entry from the relevant unit file when your configuration uses systemd. This is because an external connection to pull the container is no longer needed or available:

```
ExecStartPre=/usr/bin/docker pull $SC4S_IMAGE
```

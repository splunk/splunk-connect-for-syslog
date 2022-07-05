# Offline Container Installation

Follow these instructions to "stage" SC4S by downloading the container so that it can be loaded "out of band" on a
host machine, such as an airgapped system, without internet connectivity.

* Download container image "oci_container.tgz" from our [Github Page](https://github.com/splunk/splunk-connect-for-syslog/releases).
The following example downloads v1.12; replace the URL with the latest release or pre-release version as desired.

```
sudo wget https://github.com/splunk/splunk-connect-for-syslog/releases/download/v1.12.0/oci_container.tar.gz
```

* Distribute the container to the airgapped host machine using an appropriate file transfer utility.
* Execute the following command, using docker or podman as appropriate

```
<podman or docker> load < oci_container.tar.gz
```

* Note the container ID of the resultant load

```
Loaded image: docker.pkg.github.com/splunk/splunk-connect-for-syslog/ci:90196f77f7525bc55b3b966b5fa1ce74861c0250
```

* Use the container ID to create a local label
```
<podman or docker> tag docker.pkg.github.com/splunk/splunk-connect-for-syslog/ci:90196f77f7525bc55b3b966b5fa1ce74861c0250 sc4slocal:latest
```

* Use this local label `sc4slocal:latest` in the relevant unit or yaml file to launch SC4S (see the runtime options
above) by setting the `SC4S_IMAGE` environment variable in the unit file (example below), or the relevant `image:` tag
if using Docker Compose/Swarm.  Using this label will cause the runtime to select the locally loaded image, and will not
attempt to obtain the container image via the internet.

```
Environment="SC4S_IMAGE=sc4slocal:latest"
```
* Remove the entry
```
ExecStartPre=/usr/bin/docker pull $SC4S_IMAGE
```
from the relevant unit file when using systemd, as an external connection to pull the container is no longer needed (or available).

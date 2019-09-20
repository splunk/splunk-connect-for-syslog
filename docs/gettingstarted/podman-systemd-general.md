
# Install podman

Refer to [Installation](https://podman.io/getting-started/installation)

# Setup

* Create a systemd unit file use to start the container with the host os. ``/lib/systemd/system/sc4s.service``

*NOTE*: In a future release, the mechanism to support mounted volumes (the three -v arguments in the unit file below) will change.  For now, do not change these arguments, and ensure that the three files they reference are downloaded to the proper directory per the configuration instructions below.

*NOTE-2*: Replace the URL and HEC tokens with the appropriate values for our environment

```ini
[Unit]
Description=SC4S Container
After=network.service
Requires=network.service

[Service]
Environment="SC4S_IMAGE=splunk/sc4s:latest"

#Note Uncomment this line to use custom index names AND download the splunk_index.csv file template per getting started
Environment="SC4S_UNIT_SPLUNK_INDEX=-v /opt/sc4s/default/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv"
#Note Uncomment the following two linese for host and ip based source type mapping AND download the two file templates per getting started
#Environment="SC4S_UNIT_VP_CSV=-v /opt/sc4s/default/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv"
#Environment="SC4S_UNIT_VP_CONF=-v /opt/sc4s/default/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf"

TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/podman pull $SC4S_IMAGE
ExecStartPre=/usr/bin/podman run \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_UNIT_SPLUNK_INDEX" "$SC4S_UNIT_VP_CSV" "$SC4S_UNIT_VP_CONF" \
        --name SC4S_preflight --rm \
        $SC4S_IMAGE -s
ExecStart=/usr/bin/podman run -p 514:514 \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_UNIT_SPLUNK_INDEX"  "$SC4S_UNIT_VP_CSV" "$SC4S_UNIT_VP_CONF" \
        --name SC4S \
        --rm \
$SC4S_IMAGE

```

*NOTE*: While optional, until the final mechanism for mounted volumes in containers is released, do _not_ skip the download (wget) steps in
the configuration steps below.  Ensure these three files are in place in the directory specified, even if there is no intent to modify them.

## Configure the SC4S environment

Create the following file ``/opt/sc4s/default/env_file``

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

## Configure index destinations for Splunk

Log paths are preconfigured to utilize a convention of index destinations that is suitable for most customers. This step is optional to allow
customization of index destinations.

* Create a directory (e.g. ``/opt/sc4s/default/`` ).  Make sure the local directory references in the unit file above (the ``-v`` arguments)
match the directory you created above.  From this directory, execute the following to download the latest index context file:

```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

## Configure sources by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources which require this step refer to the "sources" section of this documentation.

* If not already done in the step immeidately above, create a directory (e.g. ``/opt/sc4s/default/`` ).  Make sure the local directory
references in the unit file above (the ``-v`` arguments) match the directory you created above.  From this directory, execute the following to
download the latest vendor context files:

```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.conf
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.csv
```
* Edit the file to identify appropriate vendor products by host glob or network mask using syslog-ng filter syntax.

# Start SC4S

```bash
sudo systemctl daemon-reload
sudo systemctl enable sc4s
sudo systemctl start sc4s
```

# Single Source Technology instance

For certain source technologies message categorization by content is impossible to support collection
of such legacy nonstandard sources we provide a means of dedicating a container to a specific source using
an alternate port.

Refer to the Sources documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example ``-p 5000-5020:5000-5020`` allows for up to 21 technology-specific ports.  Modify the individual ports or a
range as appropriate for your network.

* Modify the unit file ``/lib/systemd/system/sc4s.service``
```ini
[Unit]
Description=SC4S Container
After=network.service
Requires=network.service

[Service]
Environment="SC4S_IMAGE=splunk/scs:latest"

#Note Uncomment this line to use custom index names AND download the splunk_index.csv file template per getting started
Environment="SC4S_UNIT_SPLUNK_INDEX=-v /opt/sc4s/default/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv"
#Note Uncomment the following two linese for host and ip based source type mapping AND download the two file templates per getting started
#Environment="SC4S_UNIT_VP_CSV=-v /opt/sc4s/default/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv"
#Environment="SC4S_UNIT_VP_CONF=-v /opt/sc4s/default/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf"

TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/podman pull $SC4S_IMAGE
ExecStartPre=/usr/bin/podman run \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_UNIT_SPLUNK_INDEX" "$SC4S_UNIT_VP_CSV" "$SC4S_UNIT_VP_CONF" \
        --name SC4S_preflight --rm \
        $SC4S_IMAGE -s
ExecStart=/usr/bin/podman run -p 514:514 -p 5000-5020:5000-5020 \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_UNIT_SPLUNK_INDEX"  "$SC4S_UNIT_VP_CSV" "$SC4S_UNIT_VP_CONF" \
        --name SC4S \
        --rm \
$SC4S_IMAGE

```

Modify the following file ``/opt/sc4s/default/env_file``

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Restart SC4S.

```bash
sudo systemctl restart sc4s
```


# Install Docker CE

Refer to [Getting Started](https://docs.docker.com/get-started/)

# Setup

* Create a systemd unit file use to start the container with the host os. ``/lib/systemd/system/scs.service``

*NOTE*: The 3 volumes "-v" are optional and should be omited if the customization options are not used

*NOTE-2*: Replace the URL and HEC tokens with the appropriate values for our environment

```ini
[Unit]
Description=SCS Container
After=network.service
Requires=network.service

[Service]
Environment="SCS_IMAGE=splunk/scs:latest"

#Note Uncomment this line to use custom index names AND download the splunk_index.csv file template per getting started
Environment="SCS_UNIT_SPLUNK_INDEX=-v /opt/scs/default/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv"
#Note Uncomment the following two linese for host and ip based source type mapping AND download the two file templates per getting started
#Environment="SCS_UNIT_VP_CSV=-v /opt/scs/default/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv"
#Environment="SCS_UNIT_VP_CONF=-v /opt/scs/default/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf"

TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/docker pull $SCS_IMAGE
ExecStartPre=/usr/bin/docker run \
        --env-file=/opt/scs/default/env_file \
        "$SCS_UNIT_SPLUNK_INDEX" "$SCS_UNIT_VP_CSV" "$SCS_UNIT_VP_CONF" \
        --name scs_preflight --rm \
        $SCS_IMAGE -s
ExecStart=/usr/bin/docker run -p 514:514 \
        --env-file=/opt/scs/default/env_file \
        "$SCS_UNIT_SPLUNK_INDEX"  "$SCS_UNIT_VP_CSV" "$SCS_UNIT_VP_CONF" \
        --name scs \
        --rm \
$SCS_IMAGE
```

## Configure the SCS environment

Create the following file ``/opt/scs/default/env_file``

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
```

## Configure index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that is suitable for most customers. This step is optional to allow customization of index destinations.

* Download the latest context.csv file to a directory ``/opt/scs/default/`` 

```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

## Configure sources by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps apply to support such sources. To identify sources which require this step refer to the "sources" section of this documentation. 

* Download the latest vendor_product_by_source.conf file to a directory ``/opt/scs/default/`` 
```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.conf
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.csv
```
* Edit the file to identify appropriate vendor products by host glob or network mask using syslog-ng filter syntax.

* Start SC4S.

```bash
sudo systemctl enable scs
sudo systemctl start scs
```


# Single Source Technology instance

For certain source technologies message categorization by content is impossible to support collection 
of such legacy nonstandard sources we provide a means of dedicating a container to a specific source using
an alternate port. In the following configration example a dedicated port is opened (6514) for legacy juniper netscreen devices

Refer to the Sources documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example ``-p 5000-5020:5000-5020`` allows for up to 21 technology specific ports modify the range as appropriate

* Modify the unit file ``/opt/scs/default/env_file``
```ini
[Unit]
Description=SCS Container
After=network.service
Requires=network.service

[Service]
Environment="SCS_IMAGE=splunk/scs:latest"

#Note Uncomment this line to use custom index names AND download the splunk_index.csv file template per getting started
Environment="SCS_UNIT_SPLUNK_INDEX=-v /opt/scs/default/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv"
#Note Uncomment the following two linese for host and ip based source type mapping AND download the two file templates per getting started
#Environment="SCS_UNIT_VP_CSV=-v /opt/scs/default/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv"
#Environment="SCS_UNIT_VP_CONF=-v /opt/scs/default/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf"

TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/docker pull $SCS_IMAGE
ExecStartPre=/usr/bin/docker run \
        --env-file=/opt/scs/default/env_file \
        "$SCS_UNIT_SPLUNK_INDEX" "$SCS_UNIT_VP_CSV" "$SCS_UNIT_VP_CONF" \
        --name scs_preflight --rm \
        $SCS_IMAGE -s
ExecStart=/usr/bin/docker run -p 514:514 -p 5000-5020:5000-5020 \
        --env-file=/opt/scs/default/env_file \
        "$SCS_UNIT_SPLUNK_INDEX"  "$SCS_UNIT_VP_CSV" "$SCS_UNIT_VP_CONF" \
        --name scs \
        --rm \
$SCS_IMAGE

```

Modify the following file ``/lib/systemd/system/scs.service``

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
SCS_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
```


# Install Docker CE

Refer to [Getting Started](https://docs.docker.com/get-started/)

# Setup

* Create a systemd unit file use to start the container with the host os. ``/lib/systemd/system/scs.service``

*NOTE*: The 3 volumes "-v" are optional and should be omited if the customization options are not used

*NOTE-2*: Replace the URL and HEC tokens with the appropriate values for our environment

```ini
[Unit]
Description=Splunk Container
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/docker pull splunk/scs:latest
ExecStart=/usr/bin/docker run -p 514:514\
        -e "SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event" \
        -e "SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94" \
        -e "SPLUNK_CONNECT_METHOD=hec" \
        -e "SPLUNK_DEFAULT_INDEX=main" \
        -e "SPLUNK_METRICS_INDEX=em_metrics" \
        --name scs \
        --rm \
        -v ./sc4s-juniper/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv \
        -v ./sc4s-juniper/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv \
        -v ./sc4s-juniper/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf \
splunk/splunk:latest

[Install]
WantedBy=multi-user.target
```

## Configure index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that is suitable for most customers. This step is optional to allow customization of index destinations.

* Download the latest context.csv file to a subdirectory sc4s below the docker-compose.yml file created above

```bash
wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

## Configure sources by source IP or host name

Legacy sources and non-standard compliant source require configuration by source IP or hostname as included in the event the following steps apply to support such sources. To identify sources which require this step refer to the sources section of this documentation. 

* Download the latest vendor_product_by_source.conf file to a subdirectory sc4s below the docker-compose.yml file created above
```bash
wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.conf
```
* Edit the file to identify appropriate vendor products by host glob or network mask using syslog-ng filter syntax.

* Start SC4S

```bash
sudo systemctl enable scs
sudo systemctl start scs
```



# Install podman

Refer to [Installation](https://podman.io/getting-started/installation)

# Setup

* Create the systemd unit file `/lib/systemd/system/sc4s.service` based on the following template:

```ini
[Unit]
Description=SC4S Container
After=network.service
Requires=network.service

[Service]
Environment="SC4S_IMAGE=splunk/scs:latest"

# Optional mount point for local overrides and configurations; see notes in docs

Environment="SC4S_LOCAL_CONFIG_MOUNT=-v /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local"
# Mount point for local disk buffer
Environment="SC4S_LOCAL_DISK_BUFFER_MOUNT=-v /opt/sc4s/buffer:/opt/syslog-ng/var/data/disk-buffer"
# Uncomment the following line if custom TLS certs are provided
# Environment="SC4S_TLS_DIR=-v /opt/sc4s/tls:/opt/syslog-ng/tls"

TimeoutStartSec=0
Restart=always

ExecStartPre=/usr/bin/podman pull $SC4S_IMAGE
ExecStartPre=/usr/bin/podman run \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_LOCAL_CONFIG_MOUNT" \
        --name SC4S_preflight --rm \
        $SC4S_IMAGE -s
ExecStart=/usr/bin/podman run -p 514:514 -p 514:514/udp \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_LOCAL_CONFIG_MOUNT" \
        "$SC4S_LOCAL_DISK_BUFFER_MOUNT" \
        --name SC4S --rm \
$SC4S_IMAGE
```

* Create the subdirectory ``/opt/sc4s/local``.  This will be used as a mount point for local overrides and configurations (below).

* Create a directory on the server for disk buffer:
``/opt/syslog-ng/var/data/disk-buffer``

* NOTE: The empty ``local`` directory created above will populate with templates at the first invocation 
of SC4S for local configurations and overrides. Changes made to these files will be preserved on subsequent 
restarts (i.e. a "no-clobber" copy is performed for any missing files).  _Do not_ change the directory structure of 
the files that are laid down; change (or add) only individual files if desired.  SC4S depends on the directory layout
to read the local configurations properly.

* NOTE: You can back up the contents of this directory elsewhere and return the directory to an empty state
when a new version of SC4S is released to pick up any new changes provided by Splunk.  Upon a restart,
the direcory will populate as it did when you first installed SC4S.  Your previous changes can then
be merged back in and will take effect after another restart.

## Configure the sc4s environment

Create a file named ``/opt/sc4s/default/env_file`` and add the following environment variables:

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example.

## Modify index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that are suitable for most customers. 

* If changes need to be made to index destinations, navigate to the ``/opt/sc4s/local/context`` directory to start.
* Edit `splunk_index.csv` to review or change the index configuration and revise as required for the data sources utilized in your
environment. Simply uncomment the relevant line and enter the desired index.  The "Sources" document details the specific entries in
this table that pertain to the individual data source filters that are included with SC4S.

## Configure source filtering by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources that require this step, refer to the "sources" section of this documentation. 

* Navigate to `vendor_product_by_source.conf` and find the appropriate filter that matches your legacy device type.  
* Edit the file to properly identify these products by hostname glob or network mask using syslog-ng filter syntax.  Configuration by hostname or source IP is needed only for those devices that cannot be determined via normal syslog-ng parsing or message contents. 
* The `vendor_product_by_source.csv` file should not need to be changed unless a local filter is created that is specific to the environment.  In this case, a matching filter will also need to be provided in `vendor_product_by_source.conf`.

## Configure compliance index/metadata overrides

In some cases, devices that have been properly sourcetyped need to be further categorized by compliance, geography, or other criterion.
The two files `compliance_meta_by_source.conf` and `compliance_meta_by_source.csv` can be used for this purpose.  These operate similarly to
the files above, where the `conf` file specifies a filter to uniquely identify the messages that should be overridden, and the `csv` file
lists one or more metadata items that can be overridden based on the filter name.  This is an advanced topic, and further information is in
the "Configuration" section.

## Configure SC4S for systemd and start SC4S

```bash
sudo systemctl daemon-reload 
sudo systemctl enable sc4s
sudo systemctl start sc4s
```

# Configure Dedicated Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.  
For collection of such sources we provide a means of dedicating a unique listening port to a specific source.

Refer to the "Sources" documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example ``-p 5000-5020:5000-5020`` allows for up to 21 technology-specific ports.  Modify individual ports or a
range as appropriate for your network.

* Modify the unit file ``/lib/systemd/system/sc4s.service``
```ini
[Unit]
Description=SC4S Container
After=network.service
Requires=network.service

[Service]
Environment="SC4S_IMAGE=splunk/scs:latest"

# Optional mount point for local overrides and configurations; see notes in docs

Environment="SC4S_LOCAL_CONFIG_MOUNT=-v /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local"
# Mount point for local disk buffer
Environment="SC4S_LOCAL_DISK_BUFFER_MOUNT=-v /opt/sc4s/buffer:/opt/syslog-ng/var/data/disk-buffer"
# Uncomment the following line if custom TLS certs are provided
# Environment="SC4S_TLS_DIR=-v /opt/sc4s/tls:/opt/syslog-ng/tls"

TimeoutStartSec=0
Restart=always
ExecStartPre=/usr/bin/podman pull $SC4S_IMAGE
ExecStartPre=/usr/bin/podman run \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_LOCAL_CONFIG_MOUNT" \
        --name SC4S_preflight --rm \
        $SC4S_IMAGE -s
ExecStart=/usr/bin/podman run -p 514:514 -p 514:514/udp -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp \
        --env-file=/opt/sc4s/default/env_file \
        "$SC4S_LOCAL_CONFIG_MOUNT" \
        "$SC4S_LOCAL_DISK_BUFFER_MOUNT" \
        --name SC4S \
        --rm \
$SC4S_IMAGE
```

* Modify the following file ``/opt/sc4s/default/env_file`` to include the port-specific environment variable(s). See the "Sources" 
section for more information on your specific device(s).

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example below.

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Restart SC4S (below)

# Start SC4S

```bash
sudo systemctl start sc4s
```

# Restart SC4S

```bash
sudo systemctl restart sc4s
```

If changes were made to the configuration Unit file above (e.g. to configure with dedicated ports), you must first stop SC4S and re-run 
the systemd configuration commands:
```bash
sudo systemctl stop sc4s
sudo systemctl daemon-reload 
sudo systemctl enable sc4s
sudo systemctl start sc4s
```

# Stop SC4S

```bash
sudo systemctl stop sc4s
```
# Verify Proper Operation

SC4S has a number of "preflight" checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct.  After this step completes, to verify SC4S is properly communicating with Splunk,
execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```
This should yield the following event:
```ini
syslog-ng starting up; version='3.22.1'
``` 
when the startup process proceeds normally (without syntax errors). If you do not see this,
follow the steps below before proceeding to deeper-level troubleshooting:

* Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).

* Check to see that the proper indexes are created in Splunk, and that the token has access to them.

* Ensure the proper operation of the load balancer if used.

* Lastly, execute the following command to check the internal logs of the syslog-ng process running in the container.  Depending on the
traffic load, there may be quite a bit of output in the syslog-ng logs.
```bash
podman logs SC4S
```
You should see events similar to those below in the output:
```ini
Oct  1 03:13:35 77cd4776af41 syslog-ng[1]: syslog-ng starting up; version='3.22.1'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection accepted; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection closed; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
```
If you see http server errors such as 4xx or 5xx responses from the http (HEC) endpoint, one or more of the items above are likely set
incorrectly.  If validating/fixing the configuration fails to correct the problem, proceed to the "Troubleshooting" section for more
information.

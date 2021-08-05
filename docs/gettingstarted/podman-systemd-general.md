# Install podman

Refer to [Installation](https://podman.io/getting-started/installation)

# Initial Setup

* IMPORTANT:  Always use the _latest_ unit file (below) with the current release.  By default, the latest container is
automatically downloaded at each restart.  Therefore, make it a habit to check back here regularly to be sure any changes
that may have been made to the template unit file below (e.g. suggested mount points) are incoproprated in production prior
to relaunching via systemd.

* Create the systemd unit file `/lib/systemd/system/sc4s.service` based on the following template:

```ini
[Unit]
Description=SC4S Container
Wants=NetworkManager.service network-online.target
After=NetworkManager.service network-online.target

[Install]
WantedBy=multi-user.target

[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/splunk-connect-for-syslog:1"

# Required mount point for syslog-ng persist data (including disk buffer)
Environment="SC4S_PERSIST_MOUNT=splunk-sc4s-var:/var/lib/syslog-ng"

# Optional mount point for local overrides and configurations; see notes in docs
Environment="SC4S_LOCAL_MOUNT=/opt/sc4s/local:/etc/syslog-ng/conf.d/local:z"

# Optional mount point for local disk archive (EWMM output) files
Environment="SC4S_ARCHIVE_MOUNT=/opt/sc4s/archive:/var/lib/syslog-ng/archive:z"

# Map location of TLS custom TLS
Environment="SC4S_TLS_MOUNT=/opt/sc4s/tls:/etc/syslog-ng/tls:z"

TimeoutStartSec=0

ExecStartPre=/usr/bin/podman pull $SC4S_IMAGE
ExecStartPre=/usr/bin/bash -c "/usr/bin/systemctl set-environment SC4SHOST=$(hostname -s)"

ExecStart=/usr/bin/podman run \
        -e "SC4S_CONTAINER_HOST=${SC4SHOST}" \
        -v "$SC4S_PERSIST_MOUNT" \
        -v "$SC4S_LOCAL_MOUNT" \
        -v "$SC4S_ARCHIVE_MOUNT" \
        -v "$SC4S_TLS_MOUNT" \
        --env-file=/opt/sc4s/env_file \
        --network host \
        --name SC4S \
        --rm $SC4S_IMAGE

Restart=on-abnormal
```

* Execute the following command to create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destination(s).  This will also be used to keep track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer.  This is a required step.
```
sudo podman volume create splunk-sc4s-var
```

* NOTE:  Be sure to account for disk space requirements for the podman volume created above. This volume is located in
`/var/lib/containers/storage/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations
(typically HEC endpoints). See the "SC4S Disk Buffer Configuration" section on the Configruation page for more info.

* Create the subdirectory `/opt/sc4s/local`.  This will be used as a mount point for local overrides and configurations.

    * The empty `local` directory created above will populate with defaults and examples at the first invocation 
of SC4S for local configurations and context overrides. _Do not_ change the directory structure of 
the files that are laid down; change (or add) only individual files if desired.  SC4S depends on the directory layout
to read the local configurations properly.  See the notes below for which files will be preserved on restarts.

    * In the `local/config/` directory there are four subdirectories that allow you to provide support for device types
that are not provided out of the box in SC4S.  To get you started, there is an example log path template (`lp-example.conf.tmpl`)
and a filter (`example.conf`) in the `log_paths` and `filters` subdirectories, respectively.  These should _not_ be used directly,
but copied as templates for your own log path development.  They _will_ get overwritten at each SC4S start.

    * In the `local/context` directory, if you change the "non-example" version of a file (e.g. `splunk_metadata.csv`) the changes
will be preserved on a restart.
    
* Create the subdirectory `/opt/sc4s/archive`.  This will be used as a mount point for local storage of syslog events
(if the optional mount is uncommented above).  The events will be written in the syslog-ng EWMM format. See the "configuration"
document for details on the directory structure the archive uses.

* Create the subdirectory `/opt/sc4s/tls`.  This will be used as a mount point for custom TLS certificates
(if the optional mount is uncommented above). 
    
* IMPORTANT:  When creating the directories above, ensure the directories created match the volume mounts specified in the
unit file above.  Failure to do this will cause SC4S to abort at startup.

# Configure the sc4s environment

SC4S is almost entirely controlled through environment variables, which are read from a file at starteup.  Create a file named
`/opt/sc4s/env_file` and add the following environment variables and values:

```dotenv
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://splunk.smg.aws:8088
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no
```

* Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the correct values for your environment.  Do _not_ configure HEC
Acknowledgement when deploying the HEC token on the Splunk side; the underlying syslog-ng http destination does not support this
feature.  Moreover, HEC Ack would significantly degrade performance for streaming data such as syslog.

* The default number of `SC4S_DEST_SPLUNK_HEC_WORKERS` is 10. Consult the community if you feel the number of workers (threads) should
deviate from this.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

## Dedicated (Unique) Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.
For collection of such sources, we provide a means of dedicating a unique listening port to a specific source.

Follow this step to configure unique ports for one or more sources:

* Modify the `/opt/sc4s/env_file` file to include the port-specific environment variable(s). Refer to the "Sources"
documentation to identify the specific environment variables that are mapped to each data source vendor/technology.

## Modify index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that are suitable for most customers. 

* If changes need to be made to index destinations, navigate to the `/opt/sc4s/local/context` directory to start.
* Edit `splunk_metadata.csv` to review or change the index configuration as required for the data sources utilized in your
environment. The key (1st column) in this file uses the syntax `vendor_product`.  Simply replace the index value (the 3rd column) in the
desired row with the index appropriate for your Splunk installation. The "Sources" document details the specific `vendor_product` keys (rows)
in this table that pertain to the individual data source filters that are included with SC4S.
* Other Splunk metadata (e.g. source and sourcetype) can be overriden via this file as well.  This is an advanced topic, and further
information is covered in the "Log Path overrides" section of the Configuration document.

## Configure source filtering by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources that require this step, refer to the "sources" section of this documentation. 

* If changes need to be made to source filtering, navigate to the `/opt/sc4s/local/context` directory to start.
* Navigate to `vendor_product_by_source.conf` and find the appropriate filter that matches your legacy device type.  
* Edit the file to properly identify these products by hostname glob or network mask using syslog-ng filter syntax.  Configuration by
hostname or source IP is needed only for those devices that cannot be determined via normal syslog-ng parsing or message contents. 
* The `vendor_product_by_source.csv` file should not need to be changed unless a local log path is created that is specific to the
environment.  In this case, a matching filter will also need to be provided in `vendor_product_by_source.conf`.

## Configure compliance index/metadata overrides

In some cases, devices that have been properly sourcetyped need to be further categorized by compliance, geography, or other criterion.
The two files `compliance_meta_by_source.conf` and `compliance_meta_by_source.csv` can be used for this purpose.  These operate similarly to
the files above, where the `conf` file specifies a filter to uniquely identify the messages that should be overridden, and the `csv` file
lists one or more metadata items that can be overridden based on the filter name.  This is an advanced topic, and further information is
covered in the "Override index or metadata based on host, ip, or subnet" section of the Configuration document.

## Configure SC4S for systemd and start SC4S

```bash
sudo systemctl daemon-reload 
sudo systemctl enable sc4s
sudo systemctl start sc4s
```

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
This should yield an event similar to the following:
```ini
syslog-ng starting up; version='3.28.1'
``` 
when the startup process proceeds normally (without syntax errors). If you do not see this,
follow the steps below before proceeding to deeper-level troubleshooting:

* Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).

* Check to see that the proper indexes are created in Splunk, and that the token has access to them.

* Ensure the proper operation of the load balancer if used.

* Lastly, execute the following command to check the sc4s startup process running in the container.
```bash
podman logs SC4S
```
You should see events similar to those below in the output:
```ini
syslog-ng checking config
sc4s version=v1.36.0
starting goss
starting syslog-ng
```
If you do not see the output above, proceed to the "Troubleshooting" section for more detailed information.

# SC4S non-root operation

To operate SC4S as a user other than root, follow the instructions above, with these modifications:

## Prepare sc4s user

Create a non-root user in which to run SC4S and prepare podman for non-root operation:

```bash
sudo useradd -m -d /home/sc4s -s /bin/bash sc4s
sudo su - sc4s
mkdir -p /home/sc4s/local
mkdir -p /home/sc4s/archive
mkdir -p /home/sc4s/tls
podman system migrate
```

## Initial Setup

NOTE:  Be sure to exectute all instructions below as the SC4S user created above with the exception of changes to the unit file,
which requires sudo access.

Make the following changes to the unit file(s) configured in the main section:

* Add the name of the user created above immediately after the Service declaration, as shown in the snippet below:

```
[Service]
User=sc4s
```

* Replace all references to `/opt/sc4s` in the "Environment" declarations with `/home/sc4s`.  Make sure _not_ to change the
right-hand-side of the mount. For example:

```
Environment="SC4S_LOCAL_CONFIG_MOUNT=-v /home/sc4s/local:/etc/syslog-ng/conf.d/local:z"
```

* Replace all references to standard UDP/TCP outside listening ports (typically 514) on the _left hand side only_ of the port pairs
with arbirtrary high-numbered (> 1024) ports so that the container can listen without root privleges.  The right hand side of the pairs
(also typically 514) should remain unchanged:

```
ExecStart=/usr/bin/podman run -p 2514:514 -p 2514:514/udp -p 6514:6514 
```

If not done in the "Prepare SC4S user" above, create the three local mount directories as instructed in the main instructions,
replacing the head of the directory `/opt/sc4s` with the sc4s service user's home directory as shown below:
```
mkdir /home/sc4s/local
mkdir /home/sc4s/archive
mkdir /home/sc4s/tls
```

## Remaining Setup

The remainder of the setup can be followed directly from the main setup instructions.

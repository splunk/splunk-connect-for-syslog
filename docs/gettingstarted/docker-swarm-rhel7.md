
# Install Docker CE and Swarm (RHEL 7.7)

* Warning: this method of installing docker on RHEL is not officially supported by RedHat. Consider using podman instead.

## Enable required repositories
```bash
subscription-manager repos --enable=rhel-7-server-rpms
subscription-manager repos --enable=rhel-7-server-extras-rpms
subscription-manager repos --enable=rhel-7-server-optional-rpms
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

## Enable EPEL
```bash
yum install wget -y
cd /tmp
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
rpm -Uvh epel-release-latest-7.noarch.rpm
```

## Install required packages and enable docker
```bash
yum install docker-ce -y
systemctl enable docker.service
systemctl start docker.service
```

## Initialize Docker Swarm
```bash
sudo docker swarm init
```

# SC4S Initial Configuration

* Create a directory on the server for local configurations and disk buffering. This should be available to all administrators, for example:
`/opt/sc4s/`

* Create a docker-compose.yml file in the directory created above, based on the following template:

```yaml
version: "3.7"
services:
  sc4s:
    image: docker.io/splunk/scs:latest
    networks:
      - host
    env_file:
      - /opt/sc4s/env_file
    volumes:
      - /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z
      - splunk-sc4s-var:/opt/syslog-ng/var
# Uncomment the following line if local disk archiving is desired
#     - /opt/sc4s/archive:/opt/syslog-ng/var/archive:z
# Uncomment the following line if custom TLS certs are provided
#     - /opt/sc4s/tls:/opt/syslog-ng/tls:z

networks:
  host:
    name: host
    external: true
```

* Execute the following command to create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destination(s).  This will also be used to keep track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer.  This is a required step.
```
sudo docker volume create splunk-sc4s-var
```

* NOTE:  Be sure to account for disk space requirements for the docker volume created above. This volume is located in
`/var/lib/docker/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations
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
`docker-compose.yml` file.  Failure to do this will cause SC4S to abort at startup.

# Configure the SC4S environment

SC4S is almost entirely controlled through environment variables, which are read from a file at starteup.  Create a file named
`/opt/sc4s/env_file` and add the following environment variables and values:

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Update `SPLUNK_HEC_URL` and `SPLUNK_HEC_TOKEN` to reflect the correct values for your environment.  Do _not_ configure HEC
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

# Start/Restart SC4S

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```
# Stop SC4S

Start by obtaining the stack name (ID):
```bash
docker stack ls
```
Then, remove the stack:
```bash
docker stack rm <ID>
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
docker logs SC4S
```
You should see events similar to those below in the output:
```ini
syslog-ng checking config
sc4s version=v1.36.0
starting goss
starting syslog-ng
```
If you do not see the output above, proceed to the "Troubleshooting" section for more detailed information.

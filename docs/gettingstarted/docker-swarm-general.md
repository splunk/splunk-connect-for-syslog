
# Install Docker CE and Swarm

Refer to relevant installation guides:

* [CentOS](https://docs.docker.com/install/linux/docker-ce/centos/)
* [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
* [Debian](https://docs.docker.com/install/linux/docker-ce/debian/)
* [Desktop](https://docs.docker.com/get-started/)

NOTE:  If using a CentOS image provisioned in AWS, IPV4 forwarding is _not_ enabled by default.
This needs to be enabled for container networking to function properly.  The following is an example
to set this up; as usual this needs to be vetted with your enterprise security policy:

```sudo sysctl net.ipv4.ip_forward=1```

Then, edit /etc/sysctl.conf, find the text below, and uncomment as shown so that the change made above will survive a
reboot:

```
# Uncomment the next line to enable packet forwarding for IPv4
net.ipv4.ip_forward=1
```

# SC4S Initial Configuration

* Create a directory on the server for local configurations and disk buffering. This should be available to all
administrators, for example:
``/opt/sc4s/``

* Create a docker-compose.yml file in the directory created above, based on the following template:

```yaml
version: "3.7"
services:
  sc4s:
    image: splunk/scs:latest
    ports:  
       - target: 514
         published: 514
         protocol: tcp
# Comment the following line out if using docker-compose
         mode: host
       - target: 514
         published: 514
         protocol: udp
# Comment the following line out if using docker-compose         
         mode: host
       - target: 6514
         published: 6514
         protocol: tcp
# Comment the following line out if using docker-compose         
         mode: host         
    env_file:
      - /opt/sc4s/env_file
    volumes:
      - /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z
      - /opt/sc4s/disk-buffer:/opt/syslog-ng/var/data/disk-buffer:z
# Uncomment the following line if local disk archiving is desired
#     - /opt/sc4s/archive:/opt/syslog-ng/var/archive:z
# Uncomment the following line if custom TLS certs are provided
#     - /opt/sc4s/tls:/opt/syslog-ng/tls:z
```

* Create the subdirectory ``/opt/sc4s/local``.  This will be used as a mount point for local overrides and configurations.

    * The empty ``local`` directory created above will populate with templates at the first invocation 
of SC4S for local configurations and overrides. Changes made to these files will be preserved on subsequent 
restarts (i.e. a "no-clobber" copy is performed for any missing files).  _Do not_ change the directory structure of 
the files that are laid down; change (or add) only individual files if desired.  SC4S depends on the directory layout
to read the local configurations properly.

    * You can back up the contents of this directory elsewhere and return the directory to an empty state
when a new version of SC4S is released to pick up any new changes provided by Splunk.  Upon a restart,
the direcory will populate as it did when you first installed SC4S.  Your previous changes can then
be merged back in and will take effect after another restart.

* Create the subdirectory ``/opt/sc4s/disk-buffer``.  This will be used as a mount point for local disk buffering
of events in the event of network failure to the Splunk infrastructure.

    * This directory will populate with the disk buffer files upon SC4S startup.  If SC4S restarts for any reason, a new
    set of files will be created in addition to the original ones.  _The original ones will not be removed_.
    If you are sure, after stopping SC4S, that all data has been sent, these files can be removed.  They will be created
    again upon restart.
    
* Create the subdirectory ``/opt/sc4s/archive``.  This will be used as a mount point for local storage of syslog events
(if the optional mount is uncommented above).  The events will be written in the syslog-ng EWMM format. See the "configuration"
document for details on the directory structure the archive uses.

* Create the subdirectory ``/opt/sc4s/tls``.  This will be used as a mount point for custom TLS certificates
(if the optional mount is uncommented above). 
    
* IMPORTANT:  When creating the directories above, ensure the directories created match the volume mounts specified in the
`docker-compose.yml` file.  Failure to do this will cause SC4S to abort at startup.

# Configure the SC4S environment

SC4S is almost entirely controlled through environment variables, which are read from a file at starteup.  Create a file named
``/opt/sc4s/env_file`` and add the following environment variables and values:

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment.

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints, up to a maxiumum of 32.
If the endpoint is a VIP, match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

## Configure SC4S Listening Ports

Most enterprises use UDP/TCP port 514 as the default as their main listening port for syslog "soup" traffic, and TCP port 6514 for TLS.
The docker compose file and standard SC4S configurations reflect these defaults.  If it desired to change some or all of them, container
port mapping can be used to change the defaults without altering the underlying SC4S configuration. To do this, simply change the
``published`` port(s) in the docker compose file (which represents the actual listening ports on the host machine), like so:

```
    ports:  
       - target: 514
         published: 614
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
```
This snippet above instructs the _host_ to listen on TCP port 614 and map that port to the default TCP 514 port on the _container_.
No changes to the underlying SC4S default configuration (environment variables) are needed.

### Dedicated (Unique) Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.  
For collection of such sources, we provide a means of dedicating a unique listening port to a specific source.

The docker compose file used to start the SC4S container needs to be modified as well to reflect the additional listening ports configured
by the environment variable(s). In the following example, additional ``target`` stanzas are added for the main ``sc4s`` container, where the
``target`` and ``published`` lines provide for 21 additional technology-specific UDP and TCP ports. 

Follow these steps to configure unique ports:

* Modify the ``/opt/sc4s/env_file`` file to include the port-specific environment variable(s). Refer to the "Sources"
documentation to identify the specific environment variables that are mapped to each data source vendor/technology.
* Modify the compose file ``/opt/sc4s/docker-compose.yml`` and add/change port stanzas as appropriate using the example below.
* Restart SC4S using the command in the "Start/Restart SC4S" section below.
```yaml
version: "3.7"
services:
  sc4s:
    image: splunk/scs:latest
    ports:  
       - target: 514
         published: 514
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
       - target: 514
         published: 514
         protocol: udp
#Comment the following line out if using docker-compose         
         mode: host
       - target: 6514
         published: 6514
         protocol: tcp
# Comment the following line out if using docker-compose         
         mode: host         
       - target: 5000-5020
         published: 5000-5020
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
       - target: 5000-5020
         published: 5000-5020
         protocol: udp
#Comment the following line out if using docker-compose         
         mode: host
    env_file:
      - /opt/sc4s/env_file
    volumes:
      - /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z
      - /opt/sc4s/disk-buffer:/opt/syslog-ng/var/data/disk-buffer:z
# Uncomment the following line if local disk archiving is desired
#     - /opt/sc4s/archive:/opt/syslog-ng/var/archive:z
# Uncomment the following line if custom TLS certs are provided
#     - /opt/sc4s/tls:/opt/syslog-ng/tls:z
```

## Modify index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that are suitable for most customers. 

* If changes need to be made to index destinations, navigate to the ``/opt/sc4s/local/context`` directory to start.
* Edit `splunk_index.csv` to review or change the index configuration and revise as required for the data sources utilized in your
environment. Simply uncomment the relevant line and enter the desired index.  The "Sources" document details the specific entries in
this table that pertain to the individual data source filters that are included with SC4S.
* Other Splunk metadata (e.g. source and sourcetype) can be overriden via this file as well.  This is an advanced topic, and further
information is covered in the "Log Path overrides" section of the Configuration document.

## Configure source filtering by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources that require this step, refer to the "sources" section of this documentation. 

* If changes need to be made to source filtering, navigate to the ``/opt/sc4s/local/context`` directory to start.
* Navigate to `vendor_product_by_source.conf` and find the appropriate filter that matches your legacy device type.  
* Edit the file to properly identify these products by hostname glob or network mask using syslog-ng filter syntax.  Configuration by hostname or source IP is needed only for those devices that cannot be determined via normal syslog-ng parsing or message contents. 
* The `vendor_product_by_source.csv` file should not need to be changed unless a local filter is created that is specific to the environment.  In this case, a matching filter will also need to be provided in `vendor_product_by_source.conf`.

## Configure compliance index/metadata overrides

In some cases, devices that have been properly sourcetyped need to be further categorized by compliance, geography, or other criterion.
The two files `compliance_meta_by_source.conf` and `compliance_meta_by_source.csv` can be used for this purpose.  These operate similarly to
the files above, where the `conf` file specifies a filter to uniquely identify the messages that should be overridden, and the `csv` file
lists one or more metadata items that can be overridden based on the filter name.  This is an advanced topic, and further information is
covered in the "Override index or metadata based on host, ip, or subnet" section of the Configuration document.

# Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations.

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
docker logs SC4S
```
You should see events similar to those below in the output:
```ini
Oct  1 03:13:35 77cd4776af41 syslog-ng[1]: syslog-ng starting up; version='3.25.1'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection accepted; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection closed; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
```
If you see http server errors such as 4xx or 5xx responses from the http (HEC) endpoint, one or more of the items above are likely set
incorrectly.  If validating/fixing the configuration fails to correct the problem, proceed to the "Troubleshooting" section for more
information.

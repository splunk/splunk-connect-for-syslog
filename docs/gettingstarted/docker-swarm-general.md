
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

# SC4S Configuration

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
    env_file:
      - /opt/sc4s/env_file
    volumes:
      - /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z
      - /opt/sc4s/disk-buffer:/opt/syslog-ng/var/data/disk-buffer:z
# Uncomment the following line if custom TLS certs are provided
#     - /opt/sc4s/tls:/opt/syslog-ng/tls
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
    
* IMPORTANT:  When creating the two directories above, ensure the directories created match the volume mounts specified in the
`docker-compose.yml` file.  Failure to do this will cause SC4S to abort at startup.

## Configure the SC4S environment

Create a file named ``/opt/sc4s/env_file`` and add the following environment variables:

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment.

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

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

## Start/Restart SC4S

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```

# Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations.


# Configure Dedicated Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.  
For collection of such sources we provide a means of dedicating a unique listening port to a specific source.

Refer to the "Sources" documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example the target port ranges allow for up to 21 technology-specific ports.  Modify individual ports or a
range as appropriate for your network.

* Modify the unit file ``/opt/sc4s/docker-compose.yml``
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
#Uncomment the following line if custom TLS certs are provided
#     - /opt/sc4s/tls:/opt/syslog-ng/tls
```

* Modify the following file ``/opt/sc4s/env_file`` to include the port-specific environment variable(s).  See the "Sources" 
section for more information on your specific device(s).

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example below.

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Restart SC4S (below)

## Start/Restart SC4S

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
Oct  1 03:13:35 77cd4776af41 syslog-ng[1]: syslog-ng starting up; version='3.24.1'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection accepted; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection closed; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
```
If you see http server errors such as 4xx or 5xx responses from the http (HEC) endpoint, one or more of the items above are likely set
incorrectly.  If validating/fixing the configuration fails to correct the problem, proceed to the "Troubleshooting" section for more
information.

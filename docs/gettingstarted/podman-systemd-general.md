# Install podman

Refer to [Installation](https://podman.io/getting-started/installation)

NOTE: [READ FIRST (IPv4 forwarding)](./getting-started-runtime-configuration.md#ipv4-forwarding)

# Initial Setup

* IMPORTANT:  Always use the _latest_ unit file (below) with the current release.  By default, the latest container is
automatically downloaded at each restart.  Therefore, make it a habit to check back here regularly to be sure any changes
that may have been made to the template unit file below (e.g. suggested mount points) are incorporated in production prior
to relaunching via systemd.

* Create the systemd unit file `/lib/systemd/system/sc4s.service` based on the following template:
#### Unit file
```ini
--8<--- "docs/resources/podman/sc4s.service"
```

* Execute the following command to create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destination(s).  This will also be used to keep track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer.  This is a required step.

```
sudo podman volume create splunk-sc4s-var
```

* NOTE:  Be sure to account for disk space requirements for the podman volume created above. This volume is located in
`/var/lib/containers/storage/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations
(typically HEC endpoints). See the "SC4S Disk Buffer Configuration" section on the Configuration page for more info.

* Create subdirectories `/opt/sc4s/local` `/opt/sc4s/archive` `/opt/sc4s/tls` 

Create a file named `/opt/sc4s/env_file` and add the following environment variables and values:

```dotenv
--8<--- "docs/resources/env_file"
```

* Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the correct values for your environment.  Do _not_ configure HEC
Acknowledgement when deploying the HEC token on the Splunk side; the underlying syslog-ng http destination does not support this
feature.  Moreover, HEC Ack would significantly degrade performance for streaming data such as syslog.

* The default number of `SC4S_DEST_SPLUNK_HEC_WORKERS` is 10. Consult the community if you feel the number of workers (threads) should
deviate from this.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

For more information about configuration refer to [Docker and Podman basic configurations](./getting-started-runtime-configuration.md#docker-and-podman-basic-configurations)
and [detailed configuration](../configuration.md).

# Configure SC4S for systemd and start SC4S

```bash
sudo systemctl daemon-reload
sudo systemctl enable sc4s
sudo systemctl start sc4s
```
## Restart SC4S

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

## Stop SC4S

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

When the startup process proceeds normally (without syntax errors). If you do not see this,
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

If you do not see the output above, proceed to the ["Troubleshoot sc4s server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) sections for more detailed information.

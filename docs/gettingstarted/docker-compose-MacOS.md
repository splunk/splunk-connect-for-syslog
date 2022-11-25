
# Install Docker Desktop for MacOS

Refer to [Installation](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

# SC4S Initial Configuration

SC4S can be run with `docker-compose` or directly from the CLI with the simple `docker run` command.  Both options are outlined below.

* Create a directory on the server for local configurations and disk buffering. This should be available to all administrators, for example:
`/opt/sc4s/`

* (Optional for `docker-compose`) Create a docker-compose.yml file in the directory created above, based on the template below:

* IMPORTANT:  Always use the _latest_ compose file (below) with the current release.  By default, the latest container is
automatically downloaded at each restart.  Therefore, make it a habit to check back here regularly to be sure any changes
that may have been made to the compose template file below (e.g. suggested mount points) are incorporated in production
prior to relaunching via compose.

```yaml
--8<---- "ansible/app/docker-compose.yml"
```
* Set `/opt/sc4s` folder as shared in Docker (Settings -> Resources -> File Sharing)
* Execute the following command to create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destination(s).  This will also be used to keep track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer.  This is a required step.

```
sudo docker volume create splunk-sc4s-var
```

* NOTE:  Be sure to account for disk space requirements for the docker volume created above. This volume is located in
`/var/lib/docker/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations
(typically HEC endpoints). See the "SC4S Disk Buffer Configuration" section on the Configuration page for more info.

* IMPORTANT:  When creating the directories below, ensure the directories created match the volume mounts specified in the
`docker-compose.yml` file (if used).  Failure to do this will cause SC4S to abort at startup.

* Create subdirectories `/opt/sc4s/local` `/opt/sc4s/archive` `/opt/sc4s/tls` 

* Create a file named `/opt/sc4s/env_file` and add the following environment variables and values:

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


## Dedicated (Unique) Listening Ports
* NOTE:  Container networking differs on MacOS compared to that for linux.  On Docker Desktop, there is no "host" networking driver,
so NAT networking must be used.  For this reason, each listening port on the container must be mapped to a listening port on the host.
These port mappings are configured in the `docker-compose.yml` file or directly as a runtime option when run out of the CLI.
Be sure to update the `docker-compose.yml` file or CLI arguments when adding listening ports for new data sources.

Follow these steps to configure unique ports:

* Modify the `/opt/sc4s/env_file` file to include the port-specific environment variable(s). Refer to the "Sources"
documentation to identify the specific environment variables that are mapped to each data source vendor/technology.
* (Optional for `docker-compose`) The docker compose file used to start the SC4S container needs to be modified as well to reflect the additional listening ports configured by the environment variable(s) added above.  The docker compose file
can be amended with additional `target` stanzas in the `ports` section of the file (after the default ports). For example, the following
additional `target` and `published` lines provide for 21 additional technology-specific UDP and TCP ports:

```
       - target: 5000-5020
         published: 5000-5020
         protocol: tcp
       - target: 5000-5020
         published: 5000-5020
         protocol: udp
```

* Restart SC4S using the command in the "Start/Restart SC4S" section below.
* 
For more information about configuration refer to [Docker and Podman basic configurations](./getting-started-runtime-configuration.md#docker-and-podman-basic-configurations)
and [detailed configuration](../configuration.md).

# Start/Restart SC4S

You can use the following command to directly start SC4S if you are not using `docker-compose`.  Be sure to map the listening ports
(`-p` arguments) according to your needs:

```
/usr/bin/podman run -p 514:514 -p 514:514/udp -p 6514:6514 -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp \
    --env-file=/opt/sc4s/env_file \
    --name SC4S \
    --rm splunk/scs:latest
```

If you are using `docker-compose`, from the catalog where you created compose file execute:

```bash
docker-compose up
```
Otherwise use `docker-compose` with `-f` flag pointing to the compose file
```bash
docker-compose up -f /path/to/compose/file/docker-compose.yml
```
# Stop SC4S

If the container is run directly from the CLI, simply stop the container using the `docker stop <containerID>` command.

If using `docker-compose`, execute:

```bash
docker-compose down 
```
or 

```bash
docker-compose down -f /path/to/compose/file/docker-compose.yml
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

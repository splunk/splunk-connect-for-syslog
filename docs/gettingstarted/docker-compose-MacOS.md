
# Install Docker Desktop for MacOS

Refer to the "MacOS" section in your Docker [documentation](https://docs.docker.com) to set up your Docker Desktop for MacOS. 

# Perform your initial SC4S configuration

You can run SC4S using either `docker-compose` or the `docker run` command in the command line. This topic focuses solely on using `docker-compose`.

1. Create a directory on the server for local configurations and disk buffering. Make it available to all administrators, for example:
`/opt/sc4s/`. 

2. Create a `docker-compose.yml` file in your new directory, based on the provided template. By default, the latest container is automatically downloaded at each restart. As a best practice, consult this topic at the time of any new upgrade to check for any changes in the latest template.
``` yaml
--8<---- "ansible/app/docker-compose.yml"
```
3. In Docker Desktop, set the `/opt/sc4s` folder as shared.
4. Create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destinations. This volume also keeps track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer. Be sure to account for disk space requirements for the Docker volume. This volume is located in
`/var/lib/docker/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations. See [SC4S disk buffer configuration](https://github.com/splunk/splunk-connect-for-syslog/blob/main/docs/configuration.md#sc4s-disk-buffer-configuration) for more information.
```
sudo docker volume create splunk-sc4s-var
```

4. Create the subdirectories: `/opt/sc4s/local`, `/opt/sc4s/archive`, and `/opt/sc4s/tls`. Make sure these directories match the volume mounts specified in`docker-compose.yml`.

5. Create a file named `/opt/sc4s/env_file`.

```dotenv
--8<--- "docs/resources/env_file"
```
6. Update the following environment variables and values in `/opt/sc4s/env_file`:

* Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the values for your environment. Do not configure HEC
Acknowledgement when you deploy the HEC token on the Splunk side; syslog-ng http destination does not support this
feature. 

* The default number of `SC4S_DEST_SPLUNK_HEC_WORKERS` is 10. Consult the community if you feel the number of workers (threads) should
deviate from this.

* Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line.

## Create unique dedicated listening ports
Each listening port on the container must be mapped to a listening port on the host. Make sure to update the `docker-compose.yml` file when adding listening ports for new data sources.

To configure unique ports:

1.  Modify the `/opt/sc4s/env_file` file to include the port-specific environment variables. See the [Sources](https://splunk.github.io/splunk-connect-for-syslog/main/sources/) 
documentation to identify the specific environment variables that are mapped to each data source vendor and technology.
2. Modify the Docker Compose file that starts the SC4S container so that it reflects the additional listening ports you have created. You can amend the Docker Compose file with additional `target` stanzas in the `ports` section of the file (after the default ports). For example, the following
additional `target` and `published` lines provide for 21 additional technology-specific UDP and TCP ports:

```
       - target: 5000-5020
         published: 5000-5020
         protocol: tcp
       - target: 5000-5020
         published: 5000-5020
         protocol: udp
```

3. Restart SC4S using the command in the "Start/Restart SC4S" section in this topic.

For more information about configuration refer to [Docker and Podman basic configurations](./getting-started-runtime-configuration.md#docker-and-podman-basic-configurations)
and [detailed configuration](../configuration.md).

# Start/Restart SC4S

From the catalog where you created compose file, execute:

```bash
docker-compose up
```
Otherwise use `docker-compose` with `-f` flag pointing to the compose file
```bash
docker-compose up -f /path/to/compose/file/docker-compose.yml
```
# Stop SC4S

Execute:

```bash
docker-compose down 
```
or 

```bash
docker-compose down -f /path/to/compose/file/docker-compose.yml
```
# Verify Proper Operation

SC4S performs automatic checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once these checks are complete, verify that SC4S is properly communicating with Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

When the startup process proceeds normally, you should see an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```

If you do not see this, try the following steps to troubleshoot:

1. Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
2. Check to see that the proper indexes are created in Splunk, and that the token has access to them.
3. Ensure the proper operation of the load balancer if used.
4. Check the SC4S startup process running:

```bash
docker logs <container_name>
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

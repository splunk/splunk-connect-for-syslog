
# Install Docker Desktop

Refer to your Docker [documentation](https://docs.docker.com) to set up your Docker Desktop. 

# Perform your initial SC4S configuration

You can run SC4S with `docker-compose`, or in the command line using the command `docker run`.  Both options are described in this topic.

1. Create a directory on the server for local configurations and disk buffering. Make it available to all administrators, for example:
`/opt/sc4s/`. If you are using `docker-compose`, create a `docker-compose.yml` file in this directory using the template provided here. By default, the latest SC4S image is automatically downloaded at each restart. As a best practice, check back here regularly for any changes made to the latest template is incorporated into production before you relaunch with Docker Compose.

``` yaml
--8<---- "ansible/app/docker-compose.yml"
```

2. In Docker, set the `/opt/sc4s` folder as shared.
3. Create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destinations. This volume also keeps track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer. Be sure to account for disk space requirements for the Docker volume. This volume is located in
`/var/lib/docker/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations. See [SC4S Disk Buffer Configuration](../configuration.md#configure-your-sc4s-disk-buffer) in the Configuration topic for more information.

```
sudo docker volume create splunk-sc4s-var
```

4. Create the subdirectories: `/opt/sc4s/local`, `/opt/sc4s/archive`, and `/opt/sc4s/tls`. If you are using the `docker-compose.yml` file, make sure these directories match the volume mounts specified in`docker-compose.yml`.

5. Create a file named `/opt/sc4s/env_file`.

```dotenv
--8<--- "docs/resources/env_file"
```
6. Update the following environment variables and values to `/opt/sc4s/env_file`:

* Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the values for your environment. Do not configure HEC
Acknowledgement when you deploy the HEC token on the Splunk side; syslog-ng http destination does not support this
feature. 
* The default number of `SC4S_DEST_SPLUNK_HEC_<ID>_WORKERS` is 10. Consult the community if you feel the number of workers (threads) should
deviate from this.

NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

For more information about configuration, see [Podman + systemd](podman-systemd-general.md) and [Docker CE + systemd](docker-systemd-general.md)
and [detailed configuration](../configuration.md).

# Start or restart SC4S

* You can start SC4S directly if you are not using `docker-compose`.  Be sure to map the listening ports
(`-p` arguments) according to your needs:

```bash
docker run -p 514:514 -p 514:514/udp -p 6514:6514 -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp \
    --env-file=/opt/sc4s/env_file \
    --name SC4S \
    --rm ghcr.io/splunk/splunk-connect-for-syslog/container3:latest
```

* If you are using `docker compose`, from the catalog where you created compose file execute:
```bash
docker compose up
```

Otherwise use `docker compose` with `-f` flag pointing to the compose file:
```bash
docker compose up -f /path/to/compose/file/docker-compose.yml
```

# Stop SC4S

If the container is run directly from the CLI, stop the container using the `docker stop <containerID>` command.

If using `docker compose`, execute:

```bash
docker compose down 
```
or 

```bash
docker compose down -f /path/to/compose/file/docker-compose.yml
```
# Validate your configuration

SC4S performs automatic checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once these checks are complete, verify that SC4S is properly communicating with Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

This should yield an event similar to the following when the startup process proceeds normally:

```ini
syslog-ng starting up; version='3.28.1'
```

If you do not see this, try the following steps to troubleshoot:

1. Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
2. Check to see that the proper indexes are created in Splunk, and that the token has access to them.
3. Ensure the proper operation of the load balancer if used.
4. Check the SC4S startup process running in the container.

```bash
docker logs SC4S
```

You should see events similar to those below in the output:

```ini
syslog-ng checking config
sc4s version=v1.36.0
Configuring health check port: 8080
[2025-01-11 18:31:08 +0000] [135] [INFO] Starting gunicorn 23.0.0
[2025-01-11 18:31:08 +0000] [135] [INFO] Listening at: http://0.0.0.0:8080 (135)
[2025-01-11 18:31:08 +0000] [135] [INFO] Using worker: sync
[2025-01-11 18:31:08 +0000] [138] [INFO] Booting worker with pid: 138
starting syslog-ng
```

If you do not see the output above, see ["Troubleshoot SC4S server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) sections for more detailed information.

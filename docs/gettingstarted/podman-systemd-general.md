# Install podman

See [Podman product installation docs](https://podman.io/getting-started/installation) for information about working with your Podman installation.

Before performing the tasks described in this topic, make sure you are familiar with using IPv4 forwarding with SC4S. See [IPv4 forwarding ](./getting-started-runtime-configuration.md#ipv4-forwarding).

# Initial Setup

NOTE: Make sure to use the latest unit file, which is provided here, with the current release. By default, the latest container is
automatically downloaded at each restart. As a best practice, check back here regularly for any changes made to the latest template unit file is incorporated into production before you relaunch with systemd.

1. Create the systemd unit file `/lib/systemd/system/sc4s.service` based on the following template:

```ini
--8<--- "docs/resources/podman/sc4s.service"
```

2. Execute the following command to create a local volume, which contains the disk buffer files in the event of a communication
failure, to the upstream destinations.  This volume will also be used to keep track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer. 

```
sudo podman volume create splunk-sc4s-var
```

NOTE:  Be sure to account for disk space requirements for the podman volume you create. This volume will be located in
`/var/lib/containers/storage/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations
(typically HEC endpoints). See the "SC4S Disk Buffer Configuration" section on the Configuration page for more info.

3. Create the subdirectories:
   * `/opt/sc4s/local`
   * `/opt/sc4s/archive`
   * `/opt/sc4s/tls` 
4. Create a file named `/opt/sc4s/env_file` and add the following environment variables and values:

```dotenv
--8<--- "docs/resources/env_file"
```

5. Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the correct values for your environment.  Do not configure HEC
Acknowledgement when deploying the HEC token on the Splunk side; the underlying syslog-ng http destination does not support this
feature. The default value for `SC4S_DEST_SPLUNK_HEC_<ID>_WORKERS` is 10. Consult the community if you feel the number of workers (threads) should
deviate from this.

NOTE:  Splunk Connect for Syslog defaults to secure configurations. If you are not using trusted SSL certificates, be sure to
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

If you have made changes to the configuration unit file, for example, in order to configure dedicated ports, you must first stop SC4S and re-run
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
configuration is correct.  After this step is complete, verify SC4S is properly communicating with Splunk by
executing the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

This should yield an event similar to the following when the startup process proceeds normally (without syntax errors). 

```ini
syslog-ng starting up; version='3.28.1'
```

If you do not see this, try the following before proceeding to deeper-level troubleshooting:

* Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
* Check to see that the proper indexes are created in Splunk, and that the token has access to them.
* Ensure the proper operation of the load balancer if used.
* Execute the following command to check the sc4s startup process running in the container.

```bash
podman logs SC4S
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

If the output does not display, see ["Troubleshoot sc4s server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) for more information.

# SC4S non-root operation
### NOTE: 
Operating as a non-root user makes it impossible to use standard ports 514 and 601. Many devices cannot alter their destination port, so this operation may only be appropriate for cases where accepting syslog data from the public internet cannot be avoided.

## Prequisites
`Podman` and `slirp4netns` must be installed.


## Setup
1. Increase the number of user namespaces. Execute the following with sudo privileges:
```bash
$ echo "user.max_user_namespaces=28633" > /etc/sysctl.d/userns.conf 	 
$ sysctl -p /etc/sysctl.d/userns.conf
```

2. Create a non-root user from which to run SC4S and to prepare Podman for non-root operations:
```bash
sudo useradd -m -d /home/sc4s -s /bin/bash sc4s
sudo passwd sc4s  # type password here
sudo su - sc4s
mkdir -p /home/sc4s/local
mkdir -p /home/sc4s/archive
mkdir -p /home/sc4s/tls
podman system migrate
```

3. Load the new environment variables. To do this, temporarily switch to any other user, and then log back in as the SC4S user. When logging in as the SC4S user, don't use the 'su' command, as it won't load the new variables. Instead, you can use, for example, the command 'ssh sc4s@localhost'.

4. Create unit file in ```~/.config/systemd/user/sc4s.service``` with the following content:
```editorconfig
[Unit]
User=sc4s
Description=SC4S Container
Wants=NetworkManager.service network-online.target
After=NetworkManager.service network-online.target
[Install]
WantedBy=multi-user.target
[Service]
Environment="SC4S_IMAGE=ghcr.io/splunk/splunk-connect-for-syslog/container3:latest"
# Required mount point for syslog-ng persist data (including disk buffer)
Environment="SC4S_PERSIST_MOUNT=splunk-sc4s-var:/var/lib/syslog-ng"
# Optional mount point for local overrides and configuration
Environment="SC4S_LOCAL_MOUNT=/home/sc4s/local:/etc/syslog-ng/conf.d/local:z"
# Optional mount point for local disk archive (EWMM output) files
Environment="SC4S_ARCHIVE_MOUNT=/home/sc4s/archive:/var/lib/syslog-ng/archive:z"
# Map location of TLS custom TLS
Environment="SC4S_TLS_MOUNT=/home/sc4s/tls:/etc/syslog-ng/tls:z"
TimeoutStartSec=0
ExecStartPre=/usr/bin/podman pull $SC4S_IMAGE
# Note: The path /usr/bin/bash may vary based on your operating system.
# when startup fails on running bash check if the path is correct
ExecStartPre=/usr/bin/bash -c "/usr/bin/systemctl --user set-environment SC4SHOST=$(hostname -s)"

# Note: Prevent the error 'The container name "/SC4S" is already in use by container <container_id>. You have to remove (or rename) that container to be able to reuse that name.'
ExecStartPre=/usr/bin/bash -c "/usr/bin/podman rm SC4S > /dev/null 2>&1 || true"
ExecStart=/usr/bin/podman run -p 2514:514 -p 2514:514/udp -p 6514:6514  \
        -e "SC4S_CONTAINER_HOST=${SC4SHOST}" \
        -v "$SC4S_PERSIST_MOUNT" \
        -v "$SC4S_LOCAL_MOUNT" \
        -v "$SC4S_ARCHIVE_MOUNT" \
        -v "$SC4S_TLS_MOUNT" \
        --env-file=/home/sc4s/env_file \
        --health-cmd="/usr/sbin/syslog-ng-ctl healthcheck --timeout 5" \
        --health-interval=2m --health-retries=6 --health-timeout=5s \
        --network host \
        --name SC4S \
        --rm $SC4S_IMAGE
Restart=on-failure
```

5. Create your `env_file` file at ```/home/sc4s/env_file```
```dotenv
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=http://xxx.xxx.xxx.xxx:8088
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=xxxxxxxx
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no
SC4S_LISTEN_DEFAULT_TCP_PORT=8514
SC4S_LISTEN_DEFAULT_UDP_PORT=8514
SC4S_LISTEN_DEFAULT_RFC5426_PORT=8601
SC4S_LISTEN_DEFAULT_RFC6587_PORT=8601
```

## Run service
To run the service as a non-root user, run the `systemctl` command with `--user` flag:
```
systemctl --user daemon-reload
systemctl --user enable sc4s
systemctl --user start sc4s
```

The remainder of the setup can be found in the [main setup instructions](https://splunk.github.io/splunk-connect-for-syslog/main/gettingstarted/quickstart_guide/).

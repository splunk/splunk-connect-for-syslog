# Install Docker CE

## Before you begin

Before you start:

- Familiarize yourself with [IPv4 forwarding](./getting-started-runtime-configuration.md#ipv4-forwarding)
- Refer to installation guides for your docker configuration:
    - [CentOS](https://docs.docker.com/install/linux/docker-ce/centos/)
    - [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
    - [Debian](https://docs.docker.com/install/linux/docker-ce/debian/)

## Initial Setup

This topic provides the most recent unit file. By default, the latest SC4S image is
automatically downloaded at each restart. Consult this topic when you upgrade your SC4S installation and check for changes
to the provided template unit file. Make sure these changes are incorporated into your configuration before you relaunch with systemd.

1. Create the systemd unit file `/lib/systemd/system/sc4s.service` based on the provided template:

```ini
--8<--- "docs/resources/docker/sc4s.service"
```

2. Execute the following command to create a local volume. This volume contains the disk buffer files in case of a communication
failure to the upstream destinations:

```
sudo docker volume create splunk-sc4s-var
```

3. Account for disk space requirements for the new Docker volume. The Docker volume can grow significantly if there is an extended outage to the SC4S destinations. This volume can be found at
`/var/lib/docker/volumes/`. See [SC4S Disk Buffer Configuration](https://splunk.github.io/splunk-connect-for-syslog/main/configuration/#sc4s-disk-buffer-configuration).

4. Create the following subdirectories:

* `/opt/sc4s/local`
* `/opt/sc4s/archive`
* `/opt/sc4s/tls`


5. Create a file named `/opt/sc4s/env_file` and add the following environment variables and values:

```dotenv
--8<--- "docs/resources/env_file"
```

6. Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the correct values for your environment. Do not configure HEC
Acknowledgement when deploying the HEC token on the Splunk side, the underlying syslog-ng HTTP destination does not support this
feature. 

7. The default number of `SC4S_DEST_SPLUNK_HEC_WORKERS` is 10. Consult the community if you feel the number of workers should
deviate from this.

8. Splunk Connect for Syslog defaults to secure configurations. If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example in step 5.

For more information see [Docker and Podman basic configurations](./getting-started-runtime-configuration.md#docker-and-podman-basic-configurations)
and [detailed configuration](../configuration.md).

## Configure SC4S for systemd
To configure SC4S for systemd run the following commands:

```bash
sudo systemctl daemon-reload
sudo systemctl enable sc4s
sudo systemctl start sc4s
```
## Restart SC4S
To restart SC4S run the following command:

```bash
sudo systemctl restart sc4s
```

## Implement unit file changes
If you made changes to the configuration unit file, for example to configure with dedicated ports, you must stop SC4S and re-run the systemd configuration commands to implement your changes.

```bash
sudo systemctl stop sc4s
sudo systemctl daemon-reload 
sudo systemctl enable sc4s
sudo systemctl start sc4s
```

## Validate your configuration

SC4S performs checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once the checks are complete, validate that SC4S properly communicate with Splunk.
To do this, execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

You should see an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```

The startup process should proceed normally without syntax errors. If it does not,
follow the steps below before proceeding to deeper-level troubleshooting:

1. Verify that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
2. Verify that your indexes are created in Splunk, and that your token has access to them.
3. If you are using a load balancer, verify that it is operating properly.
4. Execute the following command to check the SC4S startup process running in the container.

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

5. If you do not see this output, see ["Troubleshoot sc4s server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) for more information.

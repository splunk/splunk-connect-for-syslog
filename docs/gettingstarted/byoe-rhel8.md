# Configure SC4S in a non-containerized SC4S deployment

Configuring SC4S in a non-containerized SC4S deployment requires a custom configuration. Note that since Splunk does not control your unique environment, we cannot help with setting up environments, debugging networking, etc. Consider this configuration only if:

* Your specific requirements preclude the use of containers or demand that you use SC4S in a custom environment.
* You have an advanced understanding of syslog-ng architectures and linux/syslog-ng
system administration.
* You have the ability to develop and automate testing in non-production environments.



This topic provides guidance for using the SC4S syslog-ng
configuration files directly on the host OS running on a hardware server or virtual machine.  You must provide:

* An appropriate host operating system, RHEL 8 is the example provided in this topic.
* An up-to-date syslog-ng installation built from source or installed from community-built RPMs.  

You must modify the base configuration for most
environments to accomodate enterprise infrastructure variations. When you upgrade, evaluate the current environment compared to this reference then develop and test an installation-specific installation plan. Do not depend on the distribution-supplied version of syslog-ng, as it may not be recent enough to support your needs.
See this [blog post](https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions)
to learn more.

# Install SC4S in a custom environment 

These installation instructions assume a recent RHEL or CentOS-based release. You may have to make minor adjustments for
Debian and Ubuntu. The examples provided here use pre-compiled binaries for the syslog-ng installation in `/etc/syslog-ng`. Your configuration may vary.

The following installation instructions are summarized from a 
[blog](https://www.syslog-ng.com/community/b/blog/posts/introducing-the-syslog-ng-stable-rpm-repositories)
maintained by the One Identity team. 

1. Install CentOS or RHEL 8.0. See your OS documentation for instructions.

2. Enable EPEL (Centos 8).

```bash
dnf install 'dnf-command(copr)' -y
dnf install epel-release -y
dnf copr enable czanik/syslog-ng336  -y
dnf install syslog-ng syslog-ng-python syslog-ng-http python3-pip gcc python3-devel -y
``` 

3. Disable the distribution-supplied syslog-ng unit file. rsyslog will continue to be the system logger, but should be left enabled only if it is not configured to 
listen on the same ports as SC4S. You can also configure SC4S to provide local logging.

```bash
sudo systemctl stop syslog-ng
sudo systemctl disable syslog-ng
```        

4. Download the latest `bare_metal.tar` from [releases](https://github.com/splunk/splunk-connect-for-syslog/releases) on github and untar the package in `/etc/syslog-ng`. This step unpacks a tarball with the SC4S version of the syslog-ng config files in the standard
`/etc/syslog-ng` location, and will overwrite existing content. Make sure that any previous configurations of syslog-ng are saved
prior to executing the download step.

For production use, select the latest version of SC4S that does not have an `-rc`, `-alpha`, or `-beta` suffix. 

```bash
sudo wget -c https://github.com/splunk/splunk-connect-for-syslog/releases/download/<latest release>/baremetal.tar -O - | sudo tar -x -C /etc/syslog-ng
```

5. Install python requirements:

```bash
sudo pip3 install -r /etc/syslog-ng/requirements.txt
```

6. You can run SC4S using systemd in one of two ways, depending on administrator preference and
orchestration methodology. These are not the only ways to run in a custom environment:

* Run the `entrypoint.sh` script (identical to that used in the container) directly using systemd.
* Alter the script to preconfigure SC4S, after which only the syslog-ng are run using systemd. 

7. To run the `entrypoint.sh` script directly in systemd, create the SC4S unit file ``/lib/systemd/system/sc4s.service`` and add the following:

```ini
[Unit]
Description=SC4S Syslog Daemon
Documentation=https://splunk-connect-for-syslog.readthedocs.io/en/latest/
Wants=network.target network-online.target
After=network.target network-online.target

[Service]
Type=simple
ExecStart=/etc/syslog-ng/entrypoint.sh
ExecReload=/bin/kill -HUP $MAINPID
EnvironmentFile=/etc/syslog-ng/env_file
StandardOutput=journal
StandardError=journal
Restart=on-abnormal

[Install]
WantedBy=multi-user.target
```

8. To run `entrypoint.sh` as a preconfigured script, modify the script by commenting out or removing the stanzas following the
`OPTIONAL for BYOE` comments in the script. This prevents syslog-ng from being launched by the script. Then create the SC4S unit file ``/lib/systemd/system/syslog-ng.service`` and add the following content:

```ini
[Unit]
Description=System Logger Daemon
Documentation=man:syslog-ng(8)
After=network.target

[Service]
Type=notify
ExecStart=/usr/sbin/syslog-ng -F $SYSLOGNG_OPTS -p /var/run/syslogd.pid
ExecReload=/bin/kill -HUP $MAINPID
EnvironmentFile=-/etc/default/syslog-ng
EnvironmentFile=-/etc/sysconfig/syslog-ng
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

9. Create the file ``/etc/syslog-ng/env_file`` and add the following environment variables. Adjust the URL/TOKEN as needed.

```dotenv
# The following "path" variables can differ from the container defaults specified in the entrypoint.sh script. 
# These are *optional* for most BYOE installations, which do not differ from the install location used.
# in the container version of SC4S.  Failure to properly set these will cause startup failure.
#SC4S_ETC=/etc/syslog-ng
#SC4S_VAR=/etc/syslog-ng/var
#SC4S_BIN=/bin
#SC4S_SBIN=/usr/sbin
#SC4S_TLS=/etc/syslog-ng/tls

# General Options
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://splunk.smg.aws:8088
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94

# Uncomment the following line if using untrusted (self-signed) SSL certificates
# SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no
```

10. Reload systemctl and restart syslog-ng (example here is shown for systemd option (1) above)

```bash
sudo systemctl daemon-reload
sudo systemctl enable sc4s
sudo systemctl start sc4s
```
## Configure SC4S listening ports

The standard SC4S configuration uses UDP/TCP port 514 as the default for the listening port for syslog traffic, and TCP port 6514 for TLS. You can change these defaults by adding the following
additional environment variables to the ``env_file``:
```dotenv
SC4S_LISTEN_DEFAULT_TCP_PORT=514
SC4S_LISTEN_DEFAULT_UDP_PORT=514
SC4S_LISTEN_DEFAULT_RFC6587_PORT=601
SC4S_LISTEN_DEFAULT_RFC5426_PORT=601
SC4S_LISTEN_DEFAULT_RFC5425_PORT=5425
SC4S_LISTEN_DEFAULT_TLS_PORT=6514
```
### Create unique dedicated listening ports

For some source technologies, categorization by message content is not possible. To collect these sources, dedicate a unique listening port to a specific source. See [Sources](https://splunk.github.io/splunk-connect-for-syslog/main/sources/) for more information.

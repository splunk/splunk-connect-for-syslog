# SC4S "Bring Your Own Environment"

* FOREWORD:  The BYOE SC4S deliverable should be considered as a self/community supported option for SC4S deployment, and should be
considered only by those with specific needs based on advanced understanding of syslog-ng architectures and linux/syslog-ng
system administration and the ability to develop and automate testing in non-production environments. The container deliverable is the most often correct deliverable of SC4S for almost all enterprises.
If you are simply trying to "get syslog working", the turnkey, container approach described in the other runtime documents will
be the fastest route to success.

The "Bring Your Own Environment" instructions that follow allow expert administrators to utilize the SC4S syslog-ng
config files directly on the host OS running on a hardware server or virtual machine.  Administrators must provide an
appropriate host OS (RHEL 8 used in this document) as well as an up-to-date syslog-ng installation either built from source (not documented here) or
installed from community-built RPMs.  Modification of the base configuration will be required for most customer
environments due to enterprise infrastructure variations. Once installed preparing an upgrade requires evaluation of the current environment compared to this reference then developing and testing a installation specific install plan. This activity is the responsibility of the administrator.

* NOTE: Installing or modifying system configurations can have unexpected consequences, and advanced linux system
administration and syslog-ng configuration experience is assumed when using the BYOE version of SC4S.

* NOTE:  Do _not_ depend on the distribution-supplied version of syslog-ng, as it will likely be far too old.
Read this [explanation](https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions)
for the reason why syslog-ng builds are so dated in almost all RHEL/Debian distributions.

# BYOE Installation Instructions

These installation instructions assume a recent RHEL or CentOS-based release.  Minor adjustments may have to be made for
Debian/Ubuntu.  In addition, almost _all_ pre-compiled binaries for syslog-ng assume installation in `/etc/syslog-ng`; these instructions
will reflect that.

The following installation instructions are summarized from a 
[blog](https://www.syslog-ng.com/community/b/blog/posts/introducing-the-syslog-ng-stable-rpm-repositories)
maintained by a developer at One Identity (formerly Balabit), who is the owner of the syslog-ng Open Source project.
It is always advisable to review the blog for the latest changes to the repo(s), as changes here are quite dynamic.

* Install CentOS or RHEL 8.0

* Enable EPEL (Centos 8)

```bash
dnf install 'dnf-command(copr)' -y
dnf install epel-release -y
dnf copr enable czanik/syslog-ng336  -y
dnf install syslog-ng syslog-ng-python syslog-ng-http python3-pip gcc python3-devel -y
``` 

* Disable the distro-supplied syslog-ng unit file, as the syslog-ng process configured here will run as the `sc4s`
service.  rsyslog will continue to be the system logger, but should be left enabled _only_ if it is configured to not
listen on the same ports as sc4s.  sc4s BYOE can be configured to provide local logging as well if desired.

```bash
sudo systemctl stop syslog-ng
sudo systemctl disable syslog-ng
```        

* Download the latest bare_metal.tar from [releases](https://github.com/splunk/splunk-connect-for-syslog/releases) on github and untar the package in `/etc/syslog-ng` using the command example below.

* NOTE:  The `wget` process below will unpack a tarball with the sc4s version of the syslog-ng config files in the standard
`/etc/syslog-ng` location, and _will_ overwrite existing content.  Ensure that any previous configurations of syslog-ng are saved
if needed prior to executing the download step.

* NOTE:  At the time of writing, the latest major release is `v1.33`.  The latest release is typically listed first on the page above, unless
there is an `-alpha`,`-beta`, or `-rc` release that is newer (which will be clearly indicated).  For production use, select the latest that does not have an `-rc`, `-alpha`, or `-beta` suffix. 

```bash
sudo wget -c https://github.com/splunk/splunk-connect-for-syslog/releases/download/<latest release>/baremetal.tar -O - | sudo tar -x -C /etc/syslog-ng
```

* Install python requirements 

```bash
sudo pip3 install -r /etc/syslog-ng/requirements.txt
```

* (Optional, for monitoring): Install `goss` and confirm that the version is v0.3.16 or newer.  `goss` installs in 
`/usr/local/bin` by default, so ensure that 1) `entrypoint.sh` is modified to include `/usr/local/bin` in the full path,
or 2) move the `goss` binary to `/bin` or `/usr/bin`.
```
curl -L https://github.com/aelsabbahy/goss/releases/latest/download/goss-linux-amd64 -o /usr/local/bin/goss
chmod +rx /usr/local/bin/goss
curl -L https://github.com/aelsabbahy/goss/releases/latest/download/dgoss -o /usr/local/bin/dgoss
# Alternatively, using the latest
# curl -L https://raw.githubusercontent.com/aelsabbahy/goss/latest/extras/dgoss/dgoss -o /usr/local/bin/dgoss
chmod +rx /usr/local/bin/dgoss
```

* There are two main options for running SC4S via systemd, the choice of which largely depends on administrator preference and
orchestration methodology: 1) the `entrypoint.sh` script (identical to that used in the container) can be run directly via systemd,
or 2) the script can be altered to preconfigure SC4S (after which only the syslog-ng are run via systemd). These
are by no means the only ways to run BYOE -- as the name implies, the method you choose will be based on your custom needs.

* To run the `entrypoint.sh` script directly in systemd, create the sc4s unit file ``/lib/systemd/system/sc4s.service`` and add the following
content:

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
Restart=always
RestartSec=30s

[Install]
WantedBy=multi-user.target
```

* To run `entrypoint.sh` as a "preconfigure" script, modify the script by commenting out or removing the stanzas following the
`OPTIONAL for BYOE` comments in the script.  This will prevent syslog-ng from being launched by the script.
Then create the sc4s unit file ``/lib/systemd/system/syslog-ng.service`` and add the following content:

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

* Create the file ``/etc/syslog-ng/env_file`` and add the following environment variables (adjusting the URL/TOKEN appropriately):

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

* Reload systemctl and restart syslog-ng (example here is shown for systemd option (1) above)

```bash
sudo systemctl daemon-reload
sudo systemctl enable sc4s
sudo systemctl start sc4s
```
## Configure SC4S Listening Ports

Most enterprises use UDP/TCP port 514 as the default as their main listening port for syslog "soup" traffic, and TCP port 6514 for TLS.
The standard SC4S configuration reflect these defaults.  These defaults can be changed by adding the following
additional environment variables with appropriate values to the ``env_file`` above:
```dotenv
SC4S_LISTEN_DEFAULT_TCP_PORT=514
SC4S_LISTEN_DEFAULT_UDP_PORT=514
SC4S_LISTEN_DEFAULT_RFC6587_PORT=601
SC4S_LISTEN_DEFAULT_RFC5426_PORT=601
SC4S_LISTEN_DEFAULT_RFC5425_PORT=5425
SC4S_LISTEN_DEFAULT_TLS_PORT=6514
```
### Dedicated (Unique) Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.
For collection of such sources we provide a means of dedicating a unique listening port to a specific source.

Refer to the "Sources" documentation to identify the specific environment variables used to enable unique listening ports for the technology
in use.

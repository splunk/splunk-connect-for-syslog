# SC4S "Bring Your Own Environment"

* FOREWORD:  The BYOE SC4S deliverable should be considered as a _secondary_ option for SC4S deployment, and should be
considered only by those with specific needs based on advanced understanding of syslog-ng architectures. The
container deliverable is the preferred deliverable of SC4S for almost all enterprises.  If you are simply trying to
"get syslog working", the turnkey, container approach described in the other runtime documents will be the fastest
route to success.

The "Bring Your Own Environment" instructions that follow allow administrators to utilize the SC4S syslog-ng
config files directly on the host OS running on a hardware server or virtual machine.  Administrators must provide an
appropriate host OS as well as an up-to-date syslog-ng installation either built from source (not documented here) or
installed from community-built RPMs.  Modification of the base configuration will be required for most customer
environments due to enterprise infrastructure variations. 

* NOTE: Installing or modifying system configurations can have unexpected consequences, and advanced linux system
administration and syslog-ng configuration experience is assumed when using the BYOE version of SC4S.

* NOTE:  Do _not_ depend on the distribution-supplied version of syslog-ng, as it will likely be far too old.
Read this [explanation](https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions)
for the reason why syslog-ng builds are so dated in almost all RHEL/Debian distributions.

# BYOE Installation Instructions

These installation instructions assume a recent RHEL or CentOS-based release.  Minor adjustments may have to be made for
Debian/Ubuntu.  In addition, almost _all_ pre-compiled binaries for syslog-ng assume installation in `etc/syslog-ng`; these instructions
will reflect that.

The following installation instructions are summarized from a 
[blog](https://www.syslog-ng.com/community/b/blog/posts/introducing-the-syslog-ng-stable-rpm-repositories)
maintained by a developer at One Identity (formerly Balabit), who is the owner of the syslog-ng Open Source project.
It is always adivisable to review the blog for the latest changes to the repo(s), as changes here are quite dynamic.

* Install CentOS or RHEL 7.7/8.0

* Enable EPEL (Centos 7)

```bash
sudo yum install epel-release
```    
    
* Enable EPEL and optional repo (RHEL 7)

```bash
cd /tmp
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum install ./epel-release-latest-*.noarch.rpm -y
sudo subscription-manager repos --enable rhel-7-server-optional-rpms
```

* Enable the "stable" unofficial repo for syslog-ng and install required packages

```bash    
cd /etc/yum.repos.d/
sudo wget https://copr.fedorainfracloud.org/coprs/czanik/syslog-ng-stable/repo/epel-7/czanik-syslog-ng-stable-epel-7.repo
sudo yum install syslog-ng syslog-ng-http syslog-ng-python 
```    

* Optional step: Disable the distro-supplied syslog-ng unit file, as the syslog-ng process configured here will run as the `sc4s`
service.  rsyslog will continue to be the system logger, but should be left enabled _only_ if it is configured to not
listen on the same ports as sc4s.  sc4s BYOE can be configured to provide local logging as well if desired.

```bash
sudo systemctl stop syslog-ng
sudo systemctl disable syslog-ng
```        

* Download the latest bare_metal.tar from [releases](https://github.com/splunk/splunk-connect-for-syslog/releases) on github and untar the package in `/etc/syslog-ng`

* NOTE:  The `wget` process below will unpack a tarball with the sc4s version of the syslog-ng config files in the standard
`/etc/syslog-ng` location, and _will_ overwrite existing content.  Ensure that any previous configurations of syslog-ng are saved
if needed prior to executing the download step.

```bash
sudo wget -c https://github.com/splunk/splunk-connect-for-syslog/releases/download/latest/baremetal.tar -O - | sudo tar -x -C /etc/syslog-ng
```

* Install gomplate and confirm that the version is 3.5.0 or newer 

```bash
sudo curl -o /usr/local/bin/gomplate -sSL https://github.com/hairyhenderson/gomplate/releases/download/v3.5.0/gomplate_linux-amd64
sudo chmod 755 /usr/local/bin/gomplate
gomplate --version
```

* Install the latest python

```scl enable rh-python36 bash```

* create the sc4s unit file ``/lib/systemd/system/sc4s.service`` and add the following content

```ini
[Unit]
Description=SC4S Syslog Daemon
Documentation=man:syslog-ng(8)
Wants=network.target network-online.target
After=network.target network-online.target

[Service]
Type=notify
ExecStartPre=/opt/sc4s/bin/preconfig.sh
ExecStart=/usr/sbin/syslog-ng -F $SYSLOGNG_OPTS -p /var/run/syslogd.pid
ExecReload=/bin/kill -HUP $MAINPID
EnvironmentFile=-/etc/default/syslog-ng
EnvironmentFile=-/etc/sysconfig/syslog-ng
EnvironmentFile=/opt/sc4s/env_file
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

* NOTE:  The `wget` process above will download a file called `entrypoint.sh` and place it in `/etc/syslog-ng`.  This is the
preconfiguration file that is used for the container version of sc4s, and forms the foundation of the BYOE version of the file you will
create below.  Do _not_ use it verbatim as there are differences between them (most notably the install location).  However, it does include
the "latest and greatest" updates from the container, and should be used (with appropriate modifications) as the basis of the contents of
`preconfig.sh` below.

* create the file ``/opt/sc4s/bin/preconfig.sh``.  This file should be made executable according to your file permission standards.
Add the following content (but be sure to check the note above to ensure the latest updates are included):

```bash
#!/usr/bin/env bash
source scl_source enable rh-python36

cd /etc/syslog-ng
#The following is no longer needed but retained as a comment just in case we run into command line length issues
#for d in $(find /opt/syslog-ng/etc -type d)
#do
#  echo Templating conf for $d
#  gomplate \
#    --input-dir=$d \
#    --template t=etc/go_templates/  \
#    --exclude=*.conf --exclude=*.csv --exclude=*.t --exclude=.*\
#    --output-map="$d/{{ .in | strings.ReplaceAll \".conf.tmpl\" \".conf\" }}"
#done

gomplate $(find . -name *.tmpl | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=go_templates/

mkdir -p /etc/syslog-ng/conf.d/local/context/
mkdir -p /etc/syslog-ng/conf.d/local/config/
cp /etc/syslog-ng/context_templates/* /etc/syslog-ng/conf.d/local/context/
for file in /etc/syslog-ng/conf.d/local/context/*.example ; do cp -v -n $file ${file%.example}; done
cp -v -R /etc/syslog-ng/local_config/* /etc/syslog-ng/conf.d/local/config/
```

* (Optional) Execute the preconfiguration shell script created above.  You may also optionally execute it as part of the unit
file, which is recommended.  If you elect _not_ to execute the script in the unit file, care must be taken to execute it manually "out of band"
when any changes are made.

```bash
sudo bash /opt/sc4s/bin/preconfig.sh 
```

* Create the file ``/opt/sc4s/env_file`` and add the following environment variables:

```dotenv
SYSLOGNG_OPTS=-f /etc/syslog-ng/syslog-ng.conf 
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Reload systemctl and restart syslog-ng

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
SC4S_LISTEN_DEFAULT_TLS_PORT=6514
```
### Dedicated (Unique) Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.
For collection of such sources we provide a means of dedicating a unique listening port to a specific source.

Refer to the "Sources" documentation to identify the specific environment variables used to enable unique listening ports for the technology
in use.

## Unique Ports for Device "Families"

Certain technology "families", such as CEF and Fortinet, are handled by a single log path in SC4S.  To set unique ports for individual
devices in a family (e.g. one each for Fortiweb and FortiOS), the container version of SC4S uses "container networking" (detailed
in the source document for the respective device families).  This, of course, is not avaialble in BYOE.  For this reason, the syslog-ng source
configuration for the extra ports that need to be mapped will need to be added manually to either the template or final "conf" version of the
respective log path file.
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
for the reason why syslog-ng builds are so dated in most RHEL/Debian distributions.

# BYOE Installation Instructions

* Install CentOS or RHEL 7.7

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

* Download the latest bare_metal.tar from [releases](https://github.com/splunk/splunk-connect-for-syslog/releases) on github and untar the package

```bash
cd /tmp
sudo wget https://github.com/splunk/splunk-connect-for-syslog/releases/download/0.12.1/baremetal.tar
tar -xf baremetal.tar 
sudo mkdir -p /opt/syslog-ng/etc
sudo mkdir -p /opt/syslog-ng/var
sudo cp -R etc/* /opt/syslog-ng/etc/
```

* Install gomplate and confirm that the version is 3.5.0 or newer 

```bash
sudo curl -o /usr/local/bin/gomplate -sSL https://github.com/hairyhenderson/gomplate/releases/download/v3.5.0/gomplate_linux-amd64
sudo chmod 755 /usr/local/bin/gomplate
gomplate --version
```

* Install the latest python

```scl enable rh-python36 bash```

* create the sc4s unit file drop in ``/etc/systemd/system/sc4s.service`` and add the following content

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

* create the file ``/opt/sc4s/bin/preconfig.sh``.  This file should be made executable according to your file permission standards. Add the following content: 

```bash
#!/usr/bin/env bash
source scl_source enable rh-python36

cd /opt/syslog-ng
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
gomplate $(find . -name *.tmpl | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=etc/go_templates/

mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp --verbose -n /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context/
cp --verbose -R -n /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/
mkdir -p /opt/syslog-ng/var/data/disk-buffer/
```

* (Optional) Execute the preconfiguration shell script created above.  You may also optionally execute it as part of the unit
file, which is recommended.  If you elect _not_ to execute the script in the unit file, care must be taken to execute it manually "out of band"
when any changes are made.

```bash
sudo bash /opt/sc4s/bin/preconfig.sh 
```

* Create the file ``/opt/sc4s/env_file`` and add the following environment variables:

```dotenv
SYSLOGNG_OPTS=-f /opt/syslog-ng/etc/syslog-ng.conf 
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

#Warning

The "Bring Your Own Environment" instructions that follow allow administrators to utilize the SC4S syslog-ng
config files directly on the host OS running on a hardware server or virtual machine.  Administrators must provide an
appropriate host OS as well as an up-to-date syslog-ng installation either built from source (not documented) or
installed from community-built RPMs.  Modification of the base configuration will be required for most customer
environments due to enterprise infrastructure variations.

* NOTE: Installing or modifying system configurations can have unexpected consequences, and rudimentary linux system
administratrion and syslog-ng configuration experience is assumed.

Read this [explanation](https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions)
on the reason syslog-ng builds are so dated in most RHEL/Debian distributions.


* Install CentOS or RHEL 7.7
* Enable EPEL 
    * Centos 7
    
    ```bash
    sudo yum install epel-release
    ```
    
    * RHEL 7 
    
    ```bash
    cd /tmp
    wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    sudo yum install ./epel-release-latest-*.noarch.rpm -y
    ```
    
* Enable the optional repo for RHEL 7 only 

    ```bash
    sudo subscription-manager repos --enable rhel-7-server-optional-rpms
    ```
* Enable the "stable" unoffical repo for syslog-ng

    ```bash    
    cd /etc/yum.repos.d/
    sudo wget https://copr.fedorainfracloud.org/coprs/czanik/syslog-ng-stable/repo/epel-7/czanik-syslog-ng-stable-epel-7.repo
    sudo yum install syslog-ng syslog-ng-http syslog-ng-python 
    ```    

* Optional step: Disable the OOB syslog-ng unit file, as the syslog-ng process configured here will run as the `sc4s`
service.  rsyslog will continue to be the system logger, and can be left enabled _only_ if it is configured to not
listen on the same ports as sc4s.  

```bash
systemctl stop syslog-ng
systemctl disable syslog-ng
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

* Install and verify gomplate verify the output is 3.5.0 or newer 

```bash
sudo curl -o /usr/local/bin/gomplate -sSL https://github.com/hairyhenderson/gomplate/releases/download/v3.5.0/gomplate_linux-amd64
sudo chmod 755 /usr/local/bin/gomplate
gomplate --help
```

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
EnvironmentFile=/opt/sc4s/default/env_file
StandardOutput=journal
StandardError=journal
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

* create the file ``/opt/sc4s/bin/preconfig.sh`` and add the following content 

```bash
#!/usr/bin/env bash
source scl_source enable rh-python36

cd /opt/syslog-ng
for d in $(find /opt/syslog-ng/etc -type d)
do
  echo Templating conf for $d
  gomplate \
    --input-dir=$d \
    --template t=etc/go_templates/  \
    --exclude=*.conf --exclude=*.csv --exclude=*.t --exclude=.*\
    --output-map="$d/{{ .in | strings.ReplaceAll \".conf.tmpl\" \".conf\" }}"
done

mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp --verbose -n /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context/
cp --verbose -R -n /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/
mkdir -p /opt/syslog-ng/var/data/disk-buffer/
```

* set execute permissions on the file
```
sudo chmod 755 /opt/sc4s/bin/preconfig.sh
```

* Create the file ``/opt/sc4s/default/env_file`` and add the following environment variables:

```dotenv
SYSLOGNG_OPTS=-f /opt/syslog-ng/etc/syslog-ng.conf 
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Reload systemctl and restart syslog-ng

```bash
sudo systemctl daemon-reload
sudo systemctl start sc4s
```

#Warning


The following guidance for configuration is designed to reproduce the SC4S container directly on the host 
OS however customer configurations can vary highly adaptation for specific customer situations is expected.

Read this [explaination](https://www.syslog-ng.com/community/b/blog/posts/installing-latest-syslog-ng-on-rhel-and-other-rpm-distributions)
on the reason syslog-ng builds are so dated in the RHEL/Debian release trees


* Install CentOS or RHEL 7.7
* Enable EPEL 
    Centos 7 
    ``sudo yum install epel-release``
    RHEL 7 
    ``
    cd /tmp
    wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
    sudo yum install ./epel-release-latest-*.noarch.rpm -y
    ``
* Enable the optional repo for RHEL 7 only 
    ``sudo subscription-manager repos --enable rhel-7-server-optional-rpms``
* Enable the "stable" unoffical repo for syslog-ng
    ``
    cd /etc/yum.repos.d/
    sudo wget https://copr.fedorainfracloud.org/coprs/czanik/syslog-ng-stable/repo/epel-7/czanik-syslog-ng-stable-epel-7.repo
    sudo yum install syslog-ng syslog-ng-http syslog-ng-python 
    ``    
* Download the latest bare_metal.tar from [releases](https://github.com/splunk/splunk-connect-for-syslog/releases) on github and untar example

``
cd /tmp
sudo wget https://github.com/splunk/splunk-connect-for-syslog/releases/download/0.12.1/baremetal.tar
tar -xf baremetal.tar 
``

* Move the configuration over the default syslog-ng configuration in /etc/syslog-ng
``
sudo cp -R etc/* /etc/syslog-ng
``

* Install and verify gomplate verify the output is 3.5.0 or newer 

``
sudo curl -o /usr/local/bin/gomplate -sSL https://github.com/hairyhenderson/gomplate/releases/download/v3.5.0/gomplate_linux-amd64
sudo chmod 755 /usr/local/bin/gomplate
gomplate --help
``

* Create a override directory for the syslog-ng unit file

``
sudo mkdir /etc/systemd/system/syslog-ng.service.d/
``

* create the sc4s unit file drop in

``sudo vi /etc/systemd/system/syslog-ng.service.d/10-sc4s.conf``

* Add the following content

``
[service]
EnvironmentFile=/opt/sc4s/default/env_file
ExecStartPre=/opt/sc4s/bin/preconfig.sh
``

* create the file ``sudo vi /opt/sc4s/bin/preconfig.sh`` and set execute permissions `sudo chmod 755 /opt/sc4s/bin/preconfig.sh`

```bash
#!/usr/bin/env bash
cd /etc/syslog-ng
for d in $(find . -type d)
do
  echo Templating conf for $d
  /usr/local/bin/gomplate \
    --input-dir=$d \
    --template t=go_templates/  \
    --exclude=*.conf --exclude=*.csv --exclude=*.t --exclude=.*\
    --output-map="$d/{{ .in | strings.ReplaceAll \".conf.tmpl\" \".conf\" }}"
done

mkdir -p conf.d/local/context/
mkdir -p conf.d/local/config/
cp --verbose -n context_templates/* conf.d/local/context/
cp --verbose -R -n local_config/* conf.d/local/config/

```
* Create a file named ``/opt/sc4s/default/env_file`` and add the following environment variables:

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```
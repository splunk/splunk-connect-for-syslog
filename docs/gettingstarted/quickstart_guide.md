# Quickstart Guide

### Splunk setup
- Create the following default indexes that are used by SC4S.
    * email
    * epav
    * netauth
    * netdlp
    * netdns
    * netfw
    * netids
    * netops
    * netwaf
    * netproxy
    * netipam
    * oswinsec
    * osnix
    * em_metrics (Optional opt-in for SC4S operational metrics; ensure this is created as a metrics index)

 * Create a HEC token for SC4S. When filling out the form for the token, it is recommended that the “Selected Indexes” pane be left blank and that a
 `lastChanceIndex` be created so that all data received by SC4S will land somewhere in Splunk.

### SC4S setup 
* Set the host OS kernel to match the default receive buffer of sc4s which is set to 16MB.
    * Add following to /etc/sysctl.conf
        ```
        net.core.rmem_default = 1703936
        net.core.rmem_max = 1703936
        ```
    * apply to the kernel\
        ``` sysctl -p```
* Ensure the kernel is not dropping packets\
    ```netstat -su | grep "receive errors"```

 * For RHEL 7/8 only install conntrack\
    ```<dnf or yum> install conntrack```

 * Create the systemd unit file `/lib/systemd/system/sc4s.service`. Copy and paste from the
[SC4S sample unit file](https://splunk-connect-for-syslog.readthedocs.io/en/master/gettingstarted/podman-systemd-general/#initial-setup
).

* Install podman or docker 
    ```
    sudo yum -y install podman
    or
    sudo yum install docker-engine -y
  ```

* Create a local volume that will contain the disk buffer files and other SC4S state files
    ```
    sudo podman volume create splunk-sc4s-var
    or 
    sudo docker volume create splunk-sc4s-var
    ```
* Create directories used as a mount point for local overrides and configurations
    ```
    mkdir /opt/sc4s/local
    mkdir /opt/sc4s/archive
    mkdir /opt/sc4s/tls
    ```
* Create the environment file `/opt/sc4s/env_file` and replace HEC_URL and HEC_TOKEN as appropriate
    ```
    SPLUNK_HEC_URL=<HEC_URL>
    SPLUNK_HEC_TOKEN=<HEC_TOKEN>
    #Uncomment the following line if using untrusted SSL certificates
    #SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
    ```
* Configure SC4S for systemd and start SC4S
    ```
    sudo systemctl daemon-reload 
    sudo systemctl enable sc4s
    sudo systemctl start sc4s
    ```
* Check podman/docker logs for errors
    ```
    sudo podman logs SC4S
    or
    sudo docker logs SC4S
    ```
* Search on Splunk for successful installation of SC4S
    ```
    index=* sourcetype=sc4s:events "starting up"
    ```
* Send sample data to default udp port 514 of SC4S machine:
  ```
  echo “Hello SC4S” > /dev/udp/<SC4S_ip>/514
   ```

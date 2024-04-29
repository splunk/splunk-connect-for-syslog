# Quickstart Guide
This guide will enable you to quickly implement basic changes to your Splunk instance and set up a simple SC4S installation. It's a great starting point for working with SC4S and establishing a minimal operational solution. The same steps are thoroughly described in the [Splunk Setup](getting-started-splunk-setup.md) and [Runtime configuration](getting-started-runtime-configuration.md) sections.

### Splunk setup
- Create the following default indexes that are used by SC4S
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
    * _metrics (Optional opt-in for SC4S operational metrics; ensure this is created as a metrics index)

 * Create a HEC token for SC4S. When filling out the form for the token, it is recommended that the “Selected Indexes” pane be left blank and that a
 `lastChanceIndex` be created so that all data received by SC4S will land somewhere in Splunk.

### SC4S setup (using RHEL 7.6)
* Set the host OS kernel to match the default receive buffer of sc4s which is set to 16MB
    * Add following to /etc/sysctl.conf
    
         ```
         net.core.rmem_default = 17039360
         net.core.rmem_max = 17039360
         ```
      
    * Apply to the kernel
    
         ```
         sysctl -p
         ```
        
* Ensure the kernel is not dropping packets

    ```
    netstat -su | grep "receive errors"
    ```

* Create the systemd unit file `/lib/systemd/system/sc4s.service`. Copy and paste from the
[SC4S sample unit file (Docker)](docker-systemd-general.md#unit-file) or [SC4S sample unit file (Podman)](podman-systemd-general.md#unit-file) .

* Install podman or docker 

    ```
    sudo yum -y install podman
    ```
    or
    ```
    sudo yum install docker-engine -y
    ```

* Create a podman/docker local volume that will contain the disk buffer files and other SC4S state files
(choose one in the command below)

    ```
    sudo podman|docker volume create splunk-sc4s-var
    ```
  
* Create directories used as a mount point for local overrides and configurations

    ```mkdir /opt/sc4s/local```

    ```mkdir /opt/sc4s/archive```

    ```mkdir /opt/sc4s/tls```
  
* Create the environment file `/opt/sc4s/env_file` and replace the HEC_URL and HEC_TOKEN as appropriate

    ```
      --8<--- "docs/resources/env_file"
    ```
  
* Configure SC4S for systemd and start SC4S

    ```sudo systemctl daemon-reload ```

    ```sudo systemctl enable sc4s```

    ```sudo systemctl start sc4s```

  
* Check podman/docker logs for errors (choose one in command below)

    ```
    sudo podman|docker logs SC4S
    ```
  
* Search on Splunk for successful installation of SC4S

    ```
    index=* sourcetype=sc4s:events "starting up"
    ```
  
* Send sample data to default udp port 514 of SC4S host

    ```
    echo “Hello SC4S” > /dev/udp/<SC4S_ip>/514
    ```

# Quickstart Guide

### Splunk setup
1. Create the following default indexes that are used by SC4S
    * `email`
    * `epav`
    * `netauth`
    * `netdlp`
    * `netdns`
    * `netfw`
    * `netids`
    * `netops`
    * `netwaf`
    * `netproxy`
    * `netipam`
    * `oswinsec`
    * `osnix`
    * '_metrics` (Optional opt-in for SC4S operational metrics; ensure this is created as a metrics index)

 2. Create a HEC token for SC4S. When filling out the form for the token, leave the “Selected Indexes” pane blank and specify that a
 `lastChanceIndex` be created so that all data received by SC4S will have a target destination in Splunk.

### SC4S setup (using RHEL 7.6)
1. Set the host OS kernel to match the default receiver buffer of SC4S, which is set to 16MB.
2. Add following to `/etc/sysctl.conf`:
    
         ```
         net.core.rmem_default = 17039360
         net.core.rmem_max = 17039360
         ```
      
3. Apply to the kernel:
    
         ```
         sysctl -p
         ```
        
4. Ensure the kernel is not dropping packets:

    ```
    netstat -su | grep "receive errors"
    ```

5. Create the systemd unit file `/lib/systemd/system/sc4s.service`. Copy and paste from the
[SC4S sample unit file (Docker)](docker-systemd-general.md#unit-file) or [SC4S sample unit file (Podman)](podman-systemd-general.md#unit-file) :

6. Install Podman or Docker:

    ```
    sudo yum -y install podman
    ```
    or
    ```
    sudo yum install docker-engine -y
    ```

7. Create a Podman/Docker local volume that will contain the disk buffer files and other SC4S state files
(choose one in the command below):

    ```
    sudo podman|docker volume create splunk-sc4s-var
    ```
  
8. Create directories to be used as a mount point for local overrides and configurations:

    ```mkdir /opt/sc4s/local```

    ```mkdir /opt/sc4s/archive```

    ```mkdir /opt/sc4s/tls```
  
9. Create the environment file `/opt/sc4s/env_file` and replace the HEC_URL and HEC_TOKEN as necessary:

    ```
      --8<--- "docs/resources/env_file"
    ```
  
10. Configure SC4S for systemd and start SC4S:

    ```sudo systemctl daemon-reload ```

    ```sudo systemctl enable sc4s```

    ```sudo systemctl start sc4s```

  
11. Check podman/docker logs for errors (choose one in command below)

    ```
    sudo podman|docker logs SC4S
    ```
  
12. Search on Splunk for successful installation of SC4S

    ```
    index=* sourcetype=sc4s:events "starting up"
    ```
  
13. Send sample data to default udp port 514 of SC4S host

    ```
    echo “Hello SC4S” > /dev/udp/<SC4S_ip>/514
    ```

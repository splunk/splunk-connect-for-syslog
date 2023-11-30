# Pluggable modules guide:

Splunk Lite's pluggable modules are predefined modules that you can enable or disable by modifying the config.yaml file. This yaml file contains a list of add-ons. See the ([config.yaml reference file](https://github.com/splunk/splunk-connect-for-syslog/blob/main/package/lite/etc/config.yaml)) for more information about this file. Once you update config.yaml you save it to /etc/syslog-ng/config.yaml.


## Install SC4S Lite using docker-compose:

The installation process is identical to the installation process for[ docker-compose for SC4S](./gettingstarted/docker-compose.md) with the following modifications.

* Use the SC4S Lite image instead of the SC4S image:
```
image: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

* Mount your config.yaml file with your add-ons to /etc/syslog-ng/config.yaml:

```
volumes:
    - /path/to/your/config.yaml:/etc/syslog-ng/config.yaml
```

**Editor's note: I feel like it might be easier for the customer if we copy the referenced installation steps in from the SC4S docs and then modify them? I took a stab below, but wasn't sure exactly where to modify the steps. Let me know what you think and we can either go with the original plan (I have edited the existing tasks) or create full tasks for docker-compose and K8S similar to the example below. I'd also be happy to set up time to talk through the installation with a developer so that I can adequately capture the steps**

*SC4S Lite can be run with docker-compose or directly from the CLI with the simple docker run command. Both options are outlined below.

1. Create a directory on the server for local configurations and disk buffering. This should be available to all administrators, for example: /opt/sc4sLite/ (Optional for docker-compose) Create a docker-compose.yaml file in the directory created above, based on the template below:

--8<---- "ansible/app/docker-compose.yml"

2. Set /opt/sc4slite folder as shared in Docker (Settings -> Resources -> File Sharing)
    
3. Execute the following command to create a local volume that will contain the disk buffer files in the event of a communication failure to the upstream destination(s). This will also be used to keep track of the state of syslog-ng between restarts, and in particular the state of the disk buffer. This is a required step.

sudo docker volume create splunk-sc4s-var

Be sure to account for disk space requirements for your docker volume. This volume is located in /var/lib/docker/volumes/. It could grow significantly if there is an extended outage to the SC4S Lite destinations. 

4. Create the directories below, and ensure the directories match the volume mounts specified in the docker-compose.yaml file (if used). Failure to do this will cause SC4S Lite to abort at startup.

    Create subdirectories /opt/sc4s/local /opt/sc4s/archive /opt/sc4s/tls

    Create a file named /opt/sc4s/env_file and add the following environment variables and values:

--8<--- "docs/resources/env_file"

5. Update SC4S_DEST_SPLUNK_HEC_DEFAULT_URL and SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN to reflect the correct values for your environment. Do not configure HEC Acknowledgement when deploying the HEC token on the Splunk side; the underlying syslog-ng http destination does not support this feature. Moreover, HEC Ack would significantly degrade performance for streaming data such as syslog.

    The default number of SC4S_DEST_SPLUNK_HEC_WORKERS is 10. Consult the community if you feel the number of workers (threads) should deviate from this.

    NOTE: Splunk Connect for Syslog defaults to secure configurations. If you are not using trusted SSL certificates, be sure to uncomment the last line in the example above.*


## Kubernetes:

The installation process is identical to the installation process for [Kubernetes for SC4S]((./gettingstarted/k8s-microk8s.md)) with the following modifications:

* Use the SC4S Lite image instead of SC4S in values.yaml:
```
image:
  repository: ghcr.io/splunk/splunk-connect-for-syslog/container3lite
```

* Mount config file. Add *addons section on sc4s* **Ed note: Where would I find this section?** section of values.yaml:

```
sc4s:
    addons:
        config.yaml: |-
            ---
            addons:
                - cisco
                - paloalto
                - dell
```

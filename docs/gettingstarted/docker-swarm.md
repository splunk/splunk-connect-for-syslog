
# Install Docker Engine

Refer to [Installation](https://docs.docker.com/engine/install/)

# SC4S Initial Configuration
NOTE: Please note that running SC4S on Docker Swarm will require additional Swarm experience, setup described below is very basic.
SC4S can be run as a stck on a docker swarm cluster. The definition of the stack is base on the docker-compose file.
One of the best advantages of running SC4S on Docker Swarm is built in mesh routing which provides out of the box load balancing and very simple scaling procedure.
To learn more about Docker Swarm load balancing (ie. using external load balancer) please refer to [docker documentation](https://docs.docker.com/engine/swarm/ingress/).

* On the manager node initiate swarm cluster: ```sudo docker swarm init --advertise-addr <manger_node_ip_address>```
  You will get registration token in response - save it.
* Register worker nodes with returned token:
  ```docker swarm join --token <registration-token> <manger_node_ip>:<port>```
* Check if the nodes were added properly- at the moment you should be seeing all nodes (manger+all registered workers):
```sudo docker node ls```

Output should be similar:

| ID                           | HOSTNAME           | STATUS |  AVAILABILITY | MANAGER STATUS | ENGINE VERSION|
|------------------------------|--------------------|--------|---------------|----------------|---------------|
| wglq9cxyu68v6q0i5z6k9f5td    | ip-xxx-xxx-xxx-xxx | Ready  |  Active       |                | 20.10.17      |
| w5832sr7ak7nwi3wyf86ygn2h    | ip-xxx-xxx-xxx-xxx | Ready  |  Active       |                | 20.10.17      |
| gpm0fdbt7yldwym53v8doimpx *  | ip-xxx-xxx-xxx-xxx | Ready  |  Active       | Leader         | 20.10.17      |


* On the manger node create following directories:``` /opt/sc4s/ /opt/sc4s/tls/ /opt/sc4s/archive/ /opt/sc4s/local```

* IMPORTANT:  When creating the directories below, ensure the directories created match the volume mounts specified in the
`docker-compose.yml` file (if used).  Failure to do this will cause SC4S to abort at startup.

* Create a file named `/opt/sc4s/env_file` and add the following environment variables and values:

```dotenv
--8<--- "docs/resources/env_file"
```
* Create a docker-compose.yml file in the directory created above, based on the template below:
``` yaml
--8<---- "docs/resources/docker-compose.yml"
```

* IMPORTANT:  Always use the _latest_ compose file (below) with the current release.  By default, the latest container is
  automatically downloaded at each restart.  Therefore, make it a habit to check back here regularly to be sure any changes
  that may have been made to the compose template file below (e.g. suggested mount points) are incorporated in production
prior to relaunching via compose.

* Execute the following command to create a local volume that will contain the disk buffer files in the event of a communication
failure to the upstream destination(s).  This will also be used to keep track of the state of syslog-ng between restarts, and in
particular the state of the disk buffer.  This is a required step.

```
sudo docker volume create splunk-sc4s-var
```

* NOTE:  Be sure to account for disk space requirements for the docker volume created above. This volume is located in
`/var/lib/docker/volumes/` and could grow significantly if there is an extended outage to the SC4S destinations
(typically HEC endpoints). See the "SC4S Disk Buffer Configuration" section on the Configuration page for more info.

* Update `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL` and `SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN` to reflect the correct values for your environment.  Do _not_ configure HEC
Acknowledgement when deploying the HEC token on the Splunk side; the underlying syslog-ng http destination does not support this
feature.  Moreover, HEC Ack would significantly degrade performance for streaming data such as syslog.

* The default number of `SC4S_DEST_SPLUNK_HEC_WORKERS` is 10. Consult the community if you feel the number of workers (threads) should
deviate from this.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

For more information about configuration refer to [Docker and Podman basic configurations](./getting-started-runtime-configuration.md#docker-and-podman-basic-configurations)
and [detailed configuration](../configuration.md).

# Start/Restart SC4S
To run sc4s stack in swarm mode run following command:
```sudo docker stack deploy --compose-file path/to/docker-compose.yml sc4s```

Verify if stack was created:
```sudo docker stack ls```

|NAME    | SERVICES | ORCHESTRATOR |
|--------|----------|--------------|
|sc4s    | 1        | Swarm        |

You can scale your number of services:
```sudo docker service update --replicas 2 sc4s_sc4s```

See services running in a given stack: 
```sudo docker stack services sc4s```

|ID            | NAME      | MODE       | REPLICAS | IMAGE                                                  | PORTS                                                            |
|--------------|-----------|------------|----------|--------------------------------------------------------|------------------------------------------------------------------|
|1xv9vvbizf3m  | sc4s_sc4s | replicated | 2/2      | ghcr.io/splunk/splunk-connect-for-syslog/container2:2  | *:514->514/tcp, *:601->601/tcp, *:6514->6514/tcp, *:514->514/udp |


# Verify Proper Operation

SC4S has a number of "preflight" checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct.  After this step completes, to verify SC4S is properly communicating with Splunk,
execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

This should yield an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```
You can verify if all services in swarm cluster are working by checking ```sc4s_container``` field in splunk- each service should be recognized by different container id. All other fields should be the same.

When the startup process proceeds normally (without syntax errors). If you do not see this,
follow the steps below before proceeding to deeper-level troubleshooting:

* Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
* Check to see that the proper indexes are created in Splunk, and that the token has access to them.
* Ensure the proper operation of the load balancer if used.
* Lastly, execute the following command to check the sc4s startup process running in the container (on the node that is hosting sc4s service).
```bash
sudo docker ps
```
You will get an ID and <image name>, next: 

```bash
docker logs <ID | image name> 
```

You should see events similar to those below in the output:

```ini
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=v1.36.0
starting goss
starting syslog-ng
```

If you do not see the output above, proceed to the ["Troubleshoot sc4s server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) sections for more detailed information.

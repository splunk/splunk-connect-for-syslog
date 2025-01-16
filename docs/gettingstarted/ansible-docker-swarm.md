SC4S installation can be automated with Ansible. To do this, you provide a list of hosts on which you want to run SC4S and the basic configuration, such as Splunk endpoint, HEC token, and TLS configuration. To perform this task, you must have existing understanding of Docker Swarm and be able to set up your Swarm architecture and configuration.

# Step 1: Prepare your initial configuration

1. Before running SC4S with Ansible, provide `env_file` with your Splunk endpoint and HEC token:

``` dotenv
--8<---- "ansible/resources/env_file"
```
2. Provide a list of hosts on which you want to run your Docker Swarm cluster and the host application in the inventory file:
``` yaml
--8<---- "ansible/inventory/inventory_swarm.yaml"
```
3. You can run your cluster with one or more manager nodes. One advantage of hosting SC4S with Docker Swarm is that you can leverage the Swarm internal load balancer. See your Swarm Mode documentation at [Docker](https://docs.docker.com). 

4. You can also provide extra service configurations, for example, the number of replicas, in the `/ansible/app/docker-compose.yml` file:
``` yaml
version: "3.7"
services:
  sc4s:
    deploy:
      replicas: 2
      ...
```
## Step 2: Deploy SC4S on your configuration
1. If you have Ansible installed on your host, run the Ansible playbook to deploy SC4S. Otherwise, use the Docker Ansible image provided in the package:
```bash
# From repository root
docker-compose -f ansible/docker-compose.yml build
docker-compose -f ansible/docker-compose.yml up -d
docker exec -it ansible_sc4s /bin/bash
```
2. If you used the Docker Ansible image in Step 1, then from your container remote shell, run the Docker Swam Ansible playbook.

* You can authenticate with username and password:
``` bash 
ansible-playbook -i path/to/inventory_swarm.yaml -u <username> --ask-pass path/to/playbooks/docker_swarm.yml
```
* Or authenticate using key pair:
``` bash 
ansible-playbook -i path/to/inventory_swarm.yaml -u <username> --key-file <key_file> path/to/playbooks/docker_swarm.yml
```

3. If your deployment is successfull, you can check the state of the Swarm cluster and deployed stack from the manager node remote shell:

* To verify that the stack is created:
```sudo docker stack ls```

|NAME    | SERVICES | ORCHESTRATOR |
|--------|----------|--------------|
|sc4s    | 1        | Swarm        |

* To scale your number of services:
```sudo docker service update --replicas 2 sc4s_sc4s```

* To see services running in a given stack: 
```sudo docker stack services sc4s```

|ID            | NAME      | MODE       | REPLICAS | IMAGE                                                 | PORTS                                                            |
|--------------|-----------|------------|----------|-------------------------------------------------------|------------------------------------------------------------------|
|1xv9vvbizf3m  | sc4s_sc4s | replicated | 2/2      | ghcr.io/splunk/splunk-connect-for-syslog/container3:latest | *:514->514/tcp, *:601->601/tcp, *:6514->6514/tcp, *:514->514/udp |


# Step 3: validate your configuration

SC4S performs checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once the checks are complete, validate that SC4S properly communicate with Splunk.
To do this, execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

You should see an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```
You can verify if all services in the Swarm cluster work by checking the ```sc4s_container``` in Splunk. Each service should have a different container ID. All other fields should be the same.

The startup process should proceed normally without syntax errors. If it does not,
follow the steps below before proceeding to deeper-level troubleshooting:

1. Verify that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
2. Verify that your indexes are created in Splunk, and that your token has access to them.
3. If you are using a load balancer, verify that it is operating properly.
4. Execute the following command to check the SC4S startup process running in the container.
   
```bash
sudo docker|podman ps
```

* You will get an ID and image name: 

```bash
docker|podman logs <ID | image name> 
```

* In the output, you should see events similar to this example:

```ini
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=v1.36.0
Configuring health check port: 8080
[2025-01-11 18:31:08 +0000] [135] [INFO] Starting gunicorn 23.0.0
[2025-01-11 18:31:08 +0000] [135] [INFO] Listening at: http://0.0.0.0:8080 (135)
[2025-01-11 18:31:08 +0000] [135] [INFO] Using worker: sync
[2025-01-11 18:31:08 +0000] [138] [INFO] Booting worker with pid: 138
starting syslog-ng
```

5. If you do not see this output, see ["Troubleshoot sc4s server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) for more information.

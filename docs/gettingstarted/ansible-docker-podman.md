## About automating SC4S installation with Ansible
You can use Ansible to automate SC4S installation. To do this you provide the host on which you want to run SC4S and some basic configuration, including:
* The Splunk endpoint
* The HEC token
* TLS configuration

# Initial Configuration

Before you run SC4S with Ansible provide the `env_file` with the Splunk endpoint and HEC token.

1. Create a file in `ansible/resources` catalog or edit [example file](/ansible/resources/env_file).

``` dotenv
--8<---- "ansible/resources/env_file"
```
2. Provide a host on which you want to run Docker Swarm cluster and host application in the inventory file:
``` yaml
--8<---- "ansible/inventory/inventory.yaml"
```
## Deploy SC4S
1. If you have ansible installed on your host, run Ansible playbook to deploy the application. Otherwise you 
can use the Docker Ansible image provided in the following package:
```bash
# From repository root
docker-compose -f ansible/docker-compose.yml build
docker-compose -f ansible/docker-compose.yml up -d
docker exec -it ansible_sc4s /bin/bash
```
2. Once you are in the container's remote shell, run the Docker Swam Ansible playbook.
To authenticate using username/password:
``` bash 
ansible-playbook -i path/to/inventory.yaml -u <username> --ask-pass path/to/playbooks/docker.yml
or
ansible-playbook -i path/to/inventory.yaml -u <username> --ask-pass path/to/playbooks/podman.yml

```
or using key pair:
``` bash 
ansible-playbook -i path/to/inventory.yaml -u <username> --key-file <key_file> path/to/playbooks/docker.yml
or
ansible-playbook -i path/to/inventory.yaml -u <username> --key-file <key_file> path/to/playbooks/podman.yml
```

# Verify Proper Operation

SC4S performs a number of "preflight" checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng configuration is correct.  

After the checks are complete, execute the following search in Splunk to verify that SC4S is properly communicating with Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

This should yield an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```
To verify that all services in a Swarm cluster are working, check the ```sc4s_container``` field in Splunk. Each service should be recognized by a different container ID. All other fields should be the same.

The startup process then proceeds normally without syntax errors. If it does not, try the following:

* Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
* Check to see that the proper indexes are created in Splunk, and that the token has access to the indexes.
* Ensure the proper operation of the load balancer if used.
* Execute the following command to check the SC4S startup process running in the container on the node that is hosting the SC4S service:
```bash
sudo docker ps
```
You will get an ID and <image name>. Next, execute: 

```bash
docker logs <ID | image name> 
```
or:
```bash
sudo systemctl status sc4s
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

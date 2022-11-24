## Notice
SC4S installation can now be automated with Ansible. All you need to do now is provide a host on which you want to run SC4S and basic configuration (Splunk endpoint, HEC token, TLS configuration, etc.).

# Initial Configuration

All you need to do before running sc4s with Ansible is providing `env_file`. In the env file provide at least proper Splunk endpoint and HEC token.
Create a file in `ansible/resources` catalog or edit [example file](ansible/resources/env_file).

``` dotenv
--8<---- "ansible/resources/env_file"
```
Next provide a host on which you want to run Docker Swarm cluster and host application in inventory file:
``` yaml
--8<---- "ansible/inventory/inventory.yaml"
```
## Deploy SC4S
Now you can run ansible playbook to deploy the application if you have ansible installed on your host
or use docker ansible image provided in the package:
```bash
# From repository root
docker-compose -f ansible/docker-compose.yml build
docker-compose -f ansible/docker-compose.yml up -d
docker exec -it ansible_sc4s /bin/bash
```
Once you are in containers remote shell you can run Docker Swam ansible playbook.
If you are authenticating via username/password:
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
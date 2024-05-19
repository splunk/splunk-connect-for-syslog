SC4S installation can be automated with Ansible. To do this, you provide a list of hosts on which you want to run SC4S and basic configuration information, such as the Splunk endpoint, HEC token, and TLS configuration.

# Step 1: Prepare your initial configuration

1. Before running SC4S with Ansible, provide `env_file` with your Splunk endpoint and HEC token:

``` dotenv
--8<---- "ansible/resources/env_file"
```
2. Provide a list of hosts on which you want to run your cluster and the host application in the inventory file:
``` yaml
--8<---- "ansible/inventory/inventory.yaml"
```
# Step 2: Deploy SC4S on your configuration
1. If you have Ansible installed on your host, run the Ansible playbook to deploy SC4S. Otherwise, use the Docker Ansible image provided in the package:
```bash
# From repository root
docker-compose -f ansible/docker-compose.yml build
docker-compose -f ansible/docker-compose.yml up -d
docker exec -it ansible_sc4s /bin/bash
```
2. If you used the Docker Ansible image in the previous step, then from your container remote shell, authenticate to and run the playbook.

* To authenticate with username and password:
``` bash 
ansible-playbook -i path/to/inventory.yaml -u <username> --ask-pass path/to/playbooks/docker.yml
or
ansible-playbook -i path/to/inventory.yaml -u <username> --ask-pass path/to/playbooks/podman.yml

```
* To authenticate using a key pair:
``` bash 
ansible-playbook -i path/to/inventory.yaml -u <username> --key-file <key_file> path/to/playbooks/docker.yml
or
ansible-playbook -i path/to/inventory.yaml -u <username> --key-file <key_file> path/to/playbooks/podman.yml
```

# Step 3: Validate your configuration

SC4S performs checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once the checks are complete, validate that SC4S properly communicate with Splunk. To do this, execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

This should yield an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```
You can verify if all SC4S instances work by checking the ```sc4s_container``` in Splunk. Each instance should have a different container ID. All other fields should be the same.

The startup process should proceed normally without syntax errors. If it does not,
follow the steps below before proceeding to deeper-level troubleshooting:

1. Verify that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
2. Verify that your indexes are created in Splunk, and that your token has access to them.
3. If you are using a load balancer, verify that it is operating properly.
4. Execute the following command to check the SC4S startup process running in the container.
```bash
sudo docker ps
```
* You will get an ID and <image name>, next: 

```bash
docker logs <ID | image name> 
```
or:
```bash
sudo systemctl status sc4s
```
* In the output, you should see events similar to this example:

```ini
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=v1.36.0
starting goss
starting syslog-ng
```

If you do not see this output, see ["Troubleshoot sc4s server"](../troubleshooting/troubleshoot_SC4S_server.md)
and ["Troubleshoot resources"](../troubleshooting/troubleshoot_resources.md) for more information.

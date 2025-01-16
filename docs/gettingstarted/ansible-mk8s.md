To automate SC4S installation with Ansible, you provide a list of hosts on which you want to run SC4S as well as basic configuration information, such as the Splunk endpoint, HEC token, and TLS configuration. To perform this task, you must have existing understanding of MicroK8s and be able to set up your Kubernetes cluster architecture and configuration.

## Step 1: Prepare your initial configuration

1. Before you run SC4S with Ansible, update `values.yaml` with your Splunk endpoint and HEC token. 
You can find the [example file here](https://github.com/splunk/splunk-connect-for-syslog/blob/main/charts/splunk-connect-for-syslog/values.yaml).

2. In the inventory file, provide a list of hosts on which you want to run your cluster and the host application:
``` yaml
--8<---- "ansible/inventory/inventory_microk8s.yaml"
```
3. Alternatively, you can spin up a high-availability cluster:
``` yaml
--8<---- "ansible/inventory/inventory_microk8s_ha.yaml"
```
## Step 2: Deploy SC4S on your configuration
1. If you have Ansible installed on your host, run the Ansible playbook to deploy SC4S. Otherwise, use the Docker Ansible image provided in the package:
```bash
# From repository root
docker-compose -f ansible/docker-compose.yml build
docker-compose -f ansible/docker-compose.yml up -d
docker exec -it ansible_sc4s /bin/bash
```
2. If you used the Docker Ansible image, then from your container remote shell, authenticate to and run the MicroK8s playbook.

* To authenticate with username and password:
``` bash 
ansible-playbook -i path/to/inventory_mk8s.yaml -u <username> --ask-pass path/to/playbooks/microk8s.yml
```

* To authenitcate if you are running a high-availability cluster:
``` bash 
ansible-playbook -i path/to/inventory_mk8s_ha.yaml -u <username> --ask-pass path/to/playbooks/microk8s_ha.yml
```

* To authenticate using a key pair:
``` bash 
ansible-playbook -i path/to/inventory_mk8s.yaml -u <username> --key-file <key_file> path/to/playbooks/microk8s.yml
```

## Step 3: Validate your configuration

SC4S performs checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once the checks are complete, validate that SC4S properly communicates with Splunk. To do this, execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

This should yield an event similar to the following:

```ini
syslog-ng starting up; version='3.28.1'
```

You can verify whether all services in the cluster work by checking the ```sc4s_container``` in Splunk. Each service should have a different container ID. All other fields should be the same.

The startup process should proceed normally without syntax errors. If it does not,
follow the steps below before proceeding to deeper-level troubleshooting:

1. Verify that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).
2. Verify that your indexes are created in Splunk, and that your token has access to them.
3. If you are using a load balancer, verify that it is operating properly.
4. Execute the following command to check the SC4S startup process running in the container.
   
```bash
sudo microk8s kubectl get pods
sudo microk8s kubectl logs <podname>
```

You should see events similar to those below in the output:

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

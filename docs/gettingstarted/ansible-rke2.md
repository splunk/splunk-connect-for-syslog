# Rancher Kubernetes Engine 2

SC4S can be deployed on Rancher Kubernetes Engine 2 (RKE). Provisioning of the infrastructure can be automated using
Ansible. This instruction assumes knowledge of RKE2 and assumes that [helm](https://helm.sh/) is installed on all control nodes. 

## Step 1: Prepare your initial configuration

1. Before you run SC4S with Ansible, update `values.yaml` with your Splunk endpoint and HEC token. 
You can find the [values.yaml file here](https://github.com/splunk/splunk-connect-for-syslog/blob/main/charts/splunk-connect-for-syslog/values.yaml).

2. In the inventory file, provide a list of hosts on which you want to run your cluster and the host application. In case of single node deployment inventory should look like this:
``` yaml
--8<---- "ansible/inventory/inventory_rke2.yml"
```

- `token_node` is the host name which must be kept unchanged. In case of high availability cluster this node is used to generate registration token. For single node deployment this feature is not used, but the `token_node` hostname is referenced in the ansible playbook.

- `ansible_host` - address of the node

- `config_file` - absolute path to the RKE2 configuration file. In most basic configuration this can be empty `.yaml` file. Different configuration variables can be found in [RKE2 documentation](https://docs.rke2.io/).

3. Alternatively, you can spin up a high-availability cluster. Variables for all hosts are the same as for single node deployment with one difference, that ansible host names for other nodes apart from `token_node` can be custom:
``` yaml
--8<---- "ansible/inventory/inventory_rke2_ha.yml"
```

For high-availability cluster some basic configuration is required inside `config_file`. Examples below show how these files should be structures, more details can be found in [RKE2 documentation](https://docs.rke2.io/install/ha):

- `token_node` configuration:
``` yaml
# The following configuration is needed only when multiple control nodes are installed inside the cluster.
tls-san:
  - my-kubernetes-domain.com
```

- Other control nodes configuration:
``` yaml
# 'token' variable should be left empty. It will be updated automatically by ansible playbook.
server: https://my-kubernetes-domain.com:9345
token:
tls-san:
  - my-kubernetes-domain.com
```

- Agent nodes configuration:
``` yaml
# 'token' variable should be left empty. It will be updated automatically by ansible playbook.
server: https://my-kubernetes-domain.com:9345
token:
```

4. Configure address pool used by Metallb in [ansible/resources/metallb-config.yaml](https://github.com/splunk/splunk-connect-for-syslog/blob/main/ansible/resources/metallb-config.yaml) file.

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
ansible-playbook -i path/to/inventory_rke2.yaml -u <username> --ask-pass path/to/playbooks/rke2.yml
```

* To authenitcate if you are running a high-availability cluster:
``` bash 
ansible-playbook -i path/to/inventory_rke2_ha.yaml -u <username> --ask-pass path/to/playbooks/rke2.yml
```

* To authenticate using a key pair:
``` bash 
ansible-playbook -i path/to/inventory_rke2.yaml -u <username> --key-file <key_file> path/to/playbooks/rke2.yml
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
kubectl get pods
kubectl logs <podname>
```

You should see events similar to those below in the output:

```ini
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=v1.36.0
starting syslog-ng
```

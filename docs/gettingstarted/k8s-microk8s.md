
# Install and configure SC4S with MicroK8s
SC4S with Microk8s leverages features of MicroK8s:

* Uses MetalLB to preserve the source IP.
* Works with any of the following operating systems: Window, Centos, rhel, Uubuntu, Debian.

Note the following:

* In deployments, Splunk supports the container and the procedural guidance for implementation. Splunk does not directly support
or provide resolutions for issues within the runtime environment.
* If you use a load balancer with one instance per host, traffic is restricted
to the entry node and only one instance of SC4S runs per node. MetalLB features will be limited and it will function as a cluster manager.

## Install and configure SC4S with MicroK8s
1. Create IP addresses. Your configuration must have at least one IP address for the host and one IP address for the internal load balancer. As a best practice, you should create three IP addresses for the host and five to ten additional addresses to use later.


2. Create an SC4S Helm repository. Use the following command to create a Helm repository to work with SC4S:

```bash
microk8s helm3 repo add splunk-connect-for-syslog https://splunk.github.io/splunk-connect-for-syslog
microk8s helm3 repo update
```

3. Create a configuration file. You can store HEC token as a kubernetes secret `values.yaml` file or HEC token value in plain text.

* To create a pain text configuration file:

```yaml
--8<---- "docs/resources/k8s/values_basic.yaml"
```

* To create a secret configuration file:

```yaml
--8<---- "docs/resources/k8s/values_basic_no_token.yaml"
```
4. Install SC4S:

```bash
microk8s helm3 install sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```
5. Install the HEC token as a kubernetes secret:
```bash
export HEC_TOKEN="00000000-0000-0000-0000-000000000000" # provide your token here!
microk8s helm3 install sc4s --set splunk.hec_token=$HEC_TOKEN splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```
# Upgrade SC4S 

To upgrade SC4S:

```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Set up high vailablity (HA) with multiple nodes

Three identically-sized nodes are required for HA. See https://microk8s.io/docs/high-availability for more information. 

1. Use the following command to set up HA:

```yaml
--8<---- "docs/resources/k8s/values_ha.yaml"
```

2. Upgrade SC4S to apply the new configuration:

```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Configure environment variables

If your configuration uses a helm based-deployment, you cannot configure environment variables and 
context files directly. Instead, use the `values.yaml` file to update your configuration.

1. Use the following command to edit the `values.yaml` file:

```yaml
--8<---- "docs/resources/k8s/values_adv.yaml"

```

2. Use the `config_files` and `context_files` variables to specify configuration and context files that are passed to SC4S.

* `config_files`: This variable contains a dictionary that maps the name of the configuration file to its content in the form of a YAML block scalar.
* `context_file`: This variable contains a dictionary that maps the name of the context files to its content in the form of a YAML block scalar. The context files `splunk_metadata.csv` and `host.csv` are passed with `values.yaml`:
  
```yaml
--8<---- "docs/resources/k8s/values_adv_config_file.yaml"
```

# Manage resources

Provision two instances per node to adjust requests and limits. This lets each instance use about 40% of each node if no other workload is present:

```yaml
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi
```


# FAQ 

# Editor's Note: Do we need this? Should it be a step? A different topic?

```bash
#we need to have a normal install of kubectl because of operator scripts
sudo snap install microk8s --classic --channel=1.24
# Basic setup of k8s
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube

su - $USER
microk8s status --wait-ready
#Note when installing metallb you will be prompted for one or more IPs to used as entry points
#Into the cluster if your plan to enable clustering this IP should not be assigned to the host (floats)
#If you do not plan to cluster then this IP may be the same IP as the host
#Note2: a single IP in cidr format is x.x.x.x/32 use CIDR or range syntax
microk8s enable dns 
microk8s enable community
microk8s enable metallb 
microk8s enable rbac 
microk8s enable storage 
microk8s enable openebs 
microk8s enable helm3
microk8s status --wait-ready

```

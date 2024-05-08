
# Install MicroK8s
The SC4S deployment model with Microk8s uses specific features of this distribution of k8s. 
While this may be reproducible with other distributions such an undertaking requires more advanced
awareness and responsibility for the administrator.

* (metalLB) ensure source IP is preserved
* Bring any operating system (window/centos/rhel/ubuntu/debian)

This configuration requires as least 2 IP addressed one for host and one for the internal load balancer. 
We suggest allocation of 3 ip addresses for the host and 5-10 addresses for later use

# FAQ
Question: How is this deployment model supported?
Answer: Similar to other deployment methods, Splunk supports the container itself and the procedural guidance for implementation but does not directly support
or otherwise provide resolutions for issues within the runtime environment. 

Question: Why is this "load balancer" ok but others are not?
Answer: While we are using a load balancer with one instance per host, the traffic is restricted
to the entry node and one instance of sc4s will run per node. This limits the function of MetalLB to 
the same function as a Cluster Manager.

Question: Is this a recommended deployment model?
Answer: Yes, the single-server microk8s model is a recommended option. The use of clustering does have additional tradeoffs and should be carefully considered
on a deployment-specific basis.

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
# Add SC4S Helm repo

```bash
microk8s helm3 repo add splunk-connect-for-syslog https://splunk.github.io/splunk-connect-for-syslog
microk8s helm3 repo update
```

# Create a config file
Dependent on whether you want to store HEC token as a kubernetes secret create `values.yaml` file. 
If you wish to provide HEC token value in plaintext configure it as in example below:

The HEC token can be configured either as a plane text or as a secret.

As Plaintext Configuration:

```yaml
--8<---- "docs/resources/k8s/values_basic.yaml"
```

As Secret Configuration:

```yaml
--8<---- "docs/resources/k8s/values_basic_no_token.yaml"
```
# Install SC4S 

```bash
microk8s helm3 install sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```
HEC token as a kubernetes secret:
```bash
export HEC_TOKEN="00000000-0000-0000-0000-000000000000" # provide your token here!
microk8s helm3 install sc4s --set splunk.hec_token=$HEC_TOKEN splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```
# Upgrade SC4S 

```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Setup for HA with multiple nodes

See https://microk8s.io/docs/high-availability

Note: Three identically-sized nodes are required for HA

```yaml
--8<---- "docs/resources/k8s/values_ha.yaml"
```

Upgrade sc4s to apply the new config

# Advanced Configuration

Using helm based deployment precludes direct configuration of environment variables and 
context files but most configuration can be set via the values.yaml

```yaml
--8<---- "docs/resources/k8s/values_adv.yaml"

```

`config_files` and `context_files` are variables used to specify configuration and context files that need to be passed to the splunk-connect-for-syslog.

`config_files`: This variable contains a dictionary that maps the name of the configuration file to its content in the form of a YAML block scalar.
`context_file`: This variable contains a dictionary that maps the name of the context files to its content in the form of a YAML block scalar. The context file named splunk_metadata.csv and host.csv are being passed with the `values.yaml`
```yaml
--8<---- "docs/resources/k8s/values_adv_config_file.yaml"
```

# Resource Management

Generally two instances will be provisioned per node adjust requests and limits to
allow each instance to use about 40% of each node presuming no other workload is present

```yaml
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

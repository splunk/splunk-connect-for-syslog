
# Install and configure SC4S with Kubernetes
Splunk provides an implementation for SC4S deployment with MicroK8s using a single-server MicroK8s as the deployment model. Clustering has some tradeoffs and should be only considered on a deployment-specific basis.

You can independently replicate the model deployment on different distributions of Kubernetes. Do not attempt this unless you have advanced understanding of Kubernetes and are willing and able to maintain this configuration regularly.

SC4S with MicroK8s leverages features of MicroK8s:
* Uses MetalLB to preserve the source IP.
* Works with any of the following operating systems: Windows, CentOS, RHEL, Ubuntu, Debian.

Splunk maintains container images, but it doesn't directly support or otherwise provide resolutions for issues within the runtime environment.

## Step 1: Allocate IP addresses
This configuration requires as least two IP addresses: one for the host and one for the internal load balancer. We suggest allocating three IP addresses for the host and 5-10 IP addresses for later use.

## Step 2: Install MicroK8s
To install MicroK8s:
```bash
sudo snap install microk8s --classic --channel=1.24
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
su - $USER
microk8s status --wait-ready
```

## Step 3: Set up your add-ons
When you install `metallb` you will be prompted for one or more IPs to use as entry points. If you do not plan to enable clustering, then this IP may be the same IP as the host. If you do plan to enable clustering this IP should not be assigned to the host.

A single IP in CIDR format is x.x.x.x/32. Use CIDR or range syntax.

```bash
microk8s enable dns 
microk8s enable community
microk8s enable metallb 
microk8s enable rbac 
microk8s enable storage 
microk8s enable openebs 
microk8s enable helm3
microk8s status --wait-ready
```

## Step 4: Add an SC4S Helm repository
To add an SC4S Helm repository:

```bash
microk8s helm3 repo add splunk-connect-for-syslog https://splunk.github.io/splunk-connect-for-syslog
microk8s helm3 repo update
```

## Step 5: Create a `values.yaml` file
Create the configuration file `values.yaml`. You can provide HEC token as a Kubernetes secret or in plain text. 

### Provide the HEC token as plain text
1. Create `values.yaml` file:

```yaml
--8<---- "docs/resources/k8s/values_basic.yaml"
```

2. Install SC4S:
```bash
microk8s helm3 install sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

### Provide the HEC token as secret
1. Create `values.yaml` file:

```yaml
--8<---- "docs/resources/k8s/values_basic_no_token.yaml"
```

2. Install SC4S:
```bash
export HEC_TOKEN="00000000-0000-0000-0000-000000000000"
microk8s helm3 install sc4s --set splunk.hec_token=$HEC_TOKEN splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Update or upgrade SC4S 
Whenever the image is upgraded or when changes are made to the `values.yaml` file and should be applied, run the command:

```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Install and configure SC4S for High Availability (HA)

Three identically-sized nodes are required for HA. See [your Microk8s documentation](https://microk8s.io) for more information.

1. Update the configuration file:
```yaml
--8<---- "docs/resources/k8s/values_ha.yaml"
```

2. Upgrade SC4S to apply the new configuration:
```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Configure your SC4S instances through `values.yaml`

With helm-based deployment you cannot configure environment variables and 
context files directly. Instead, use the `values.yaml` file to update your configuration, for example:

```yaml
--8<---- "docs/resources/k8s/values_adv.yaml"

```

Use the `config_files` and `context_files` variables to specify configuration and context files that are passed to SC4S.

- `config_files`: This variable contains a dictionary that maps the name of the configuration file to its content in the form of a YAML block scalar.
- `context_file`: This variable contains a dictionary that maps the name of the context files to its content in the form of a YAML block scalar. The context files `splunk_metadata.csv` and `host.csv` are passed with `values.yaml`:
```yaml
--8<---- "docs/resources/k8s/values_adv_config_file.yaml"
```

# Manage resources

You should expect your system to require two instances per node by default. Adjust requests and limits to allow each instance to use about 40% of each node, presuming no other workload is present. 

```yaml
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

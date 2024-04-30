
# Install and configure SC4S with Kubernetes
Splunk provides procedural implementation for SC4S deployment with Microk8s. The single-server Microk8s is a recommended deployment model. The use of clustering does have additional tradeoffs and should be carefully considered on a deployment-specific basis.

Administrators have the ability to independently replicate the model deployment on different distributions of Kubernetes, however, that requires more advanced awareness and responsibility for the administrator.

SC4S with Microk8s leverages features of MicroK8s:
* Uses MetalLB to preserve the source IP.
* Works with any of the following operating systems: Windows, CentOS, RHEL, Ubuntu, Debian.

Splunk maintains container images, but it doesn't directly support or otherwise provide resolutions for issues within the runtime environment.

## Allocate IPs
This configuration requires as least 2 IP addresses: one for host and one for the internal load balancer. 
We suggest allocation of 3 IP addresses for the host and 5-10 addresses for later use.

## Install Microk8s
```bash
sudo snap install microk8s --classic --channel=1.24
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
su - $USER
microk8s status --wait-ready
```

## Setup addons
Note: when installing `metallb` you will be prompted for one or more IPs to use as entry points. If you do not plan to cluster then this IP may be the same IP as the host. If you plan to enable clustering this IP should not be assigned to the host.

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

## Add SC4S Helm repo

```bash
microk8s helm3 repo add splunk-connect-for-syslog https://splunk.github.io/splunk-connect-for-syslog
microk8s helm3 repo update
```

## Create a `values.yaml` file
Create a configuration file: `values.yaml`. You can provide HEC token as a Kubernetes secret or in plain text. Follow your chosen procedure.

### HEC token as plaintext
1. Create `values.yaml` file

```yaml
--8<---- "docs/resources/k8s/values_basic.yaml"
```

2. Install SC4S
```bash
microk8s helm3 install sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

### HEC token as secret
1. Create `values.yaml` file

```yaml
--8<---- "docs/resources/k8s/values_basic_no_token.yaml"
```

2. Install SC4S
```bash
export HEC_TOKEN="00000000-0000-0000-0000-000000000000"
microk8s helm3 install sc4s --set splunk.hec_token=$HEC_TOKEN splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

### Update/upgrade SC4S 
Whenever the image should be upgraded or changes in the `values.yaml` file should be applied, run the command:

```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Install and configure SC4S for High Availability (HA)

Three identically-sized nodes are required for HA. See [Microk8s documentation](https://microk8s.io/docs/high-availability) for more information.

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

Generally two instances will be provisioned per node. Adjust requests and limits to
allow each instance to use about 40% of each node presuming no other workload is present.

```yaml
resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

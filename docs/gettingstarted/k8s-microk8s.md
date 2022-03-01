
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
sudo snap install kubectl --classic 
# Basic setup of k8s
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube

su - $USER
microk8s status --wait-ready
#Note when installing metallb you will be prompted for one or more IPs to used as entry points
#Into the cluster if your plan to enable clustering this IP should not be assigned to the host (floats)
#If you do not plan to cluster then this IP may be the same IP as the host
#Note2: a single IP in cidr format is x.x.x.x/32 use CIDR or range syntax
microk8s enable dns metallb rbac storage openebs helm3
microk8s status --wait-ready
#
```
# Add SC4S Helm repo

```bash
microk8s helm3 repo add splunk-connect-for-syslog https://splunk.github.io/splunk-connect-for-syslog
microk8s helm3 repo update
```

# Create a config file

```yaml
#values.yaml
splunk:
    hec_url: "https://10.202.32.101:8088/services/collector/event"
    hec_token: "00000000-0000-0000-0000-000000000000"
    hec_verify_tls: "yes"
```

# Install SC4S 

```bash
microk8s helm3 install sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Upgrade SC4S 

```bash
microk8s helm3 upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog -f values.yaml
```

# Setup for HA with multiple nodes

See https://microk8s.io/docs/high-availability

Note: Three identically-sized nodes are required for HA

```yaml
#values.yaml
replicaCount: 6 #2x node count
splunk:
    hec_url: "https://10.202.32.101:8088/services/collector/event"
    hec_token: "00000000-0000-0000-0000-000000000000"
    hec_verify_tls: "yes"
```

Upgrade sc4s to apply the new config

# Advanced Configuration

Using helm based deployment precludes direct configuration of environment variables and 
context files but most configuration can be set via the values.yaml

```yaml
sc4s: 
  # Certificate as a k8s Secret with tls.key and tls.crt fields
  # Ideally produced and managed by cert-manager.io
  existingCert: example-com-tls
  #
  vendor_product:
    - name: checkpoint
      ports:
        tcp: [9000] #Same as SC4S_LISTEN_CHECKPOINT_TCP_PORT=9000
        udp: [9000]
      options:
        listen:
          old_host_rules: "yes" #Same as SC4S_LISTEN_CHECKPOINT_OLD_HOST_RULES=yes

    - name: infoblox
      ports:
        tcp: [9001, 9002]
        tls: [9003]
    - name: fortinet
      ports:
        ietf_udp:
          - 9100
          - 9101
  context_files:
    splunk_metadata.csv: |-
      cisco_meraki,index,foo
    host.csv: |-
      192.168.1.1,foo
      192.168.1.2,moon
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

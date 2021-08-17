
# Install MicroK8s

The SC4S deployment model with Microk8s uses specific features of this distribution of k8s. 
While this may be reproducable with other distributions such an undertaking requires more advanced
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
microk8s enable dns metallb rbac storage openebs
microk8s status --wait-ready
mkdir ~/.kube
#tell the default install of kubectl how to talk to our cluster
microk8s.config > $HOME/.kube/config
#
```

# Install SC4S

```bash
git clone https://github.com/splunk/splunk-connect-for-syslog.git
cd splunk-connect-for-syslog
kubectl create ns sc4s
kubectl apply -n sc4s -f deploy/k8s-microk8s/sc4s-infra.yaml
# Important modify the following command to use the correct token
echo -n 'A8AE530F-73C6-E990-704A-963E3623F4D0' > hec_token.txt
kubectl create -n sc4s secret generic sc4s-secrets --from-file=hec_token=./hec_token.txt
rm hec_token.txt
# Edit the values for SC4S_DEST_SPLUNK_HEC_DEFAULT_URL and SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY
kubectl edit -n sc4s configmap sc4s-env-file 
# Deploy sc4s
kubectl apply -n sc4s -f deploy/k8s-microk8s/sc4s-deploy.yaml
# Watch pods use ctrl + c to terminate when running
kubectl get -n sc4s pods -w
# Optional get logs replace with pod name above
kubectl -n sc4s logs splunk-sc4s-22rr6  
```

Check Splunk for events

# Change configuration

Note change change to the following config; this will trigger a restart of the container

```bash
kubectl edit configmap sc4s-env-file
kubectl edit configmap sc4s-context-config
```

# Setup for HA with multiple nodes

See https://microk8s.io/docs/high-availability

Note: Three identically-sized nodes are required for HA

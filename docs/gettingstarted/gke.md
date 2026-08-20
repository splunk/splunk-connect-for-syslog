You can install SC4S on Google Cloud Platform with GKE (Google Kubernetes Engine). To do this, you can use the SC4S Helm chart with GCP-specific configuration.

Refer to the GCP documentation for the following setup steps before proceeding:

- [Enable Kubernetes Engine API](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-regional-cluster#before_you_begin)
- [Create a VPC network](https://cloud.google.com/vpc/docs/create-modify-vpc-networks#create-auto-network) (required if your project has no default network)
- [Create a regional GKE cluster](https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-regional-cluster)
- [Configure kubectl access to your cluster](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl)

Before you begin you also need to have `kubectl` and `helm` installed. Both are pre-installed in [GCP Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell) — a browser-based terminal available in the GCP Console.

!!! note
    GCP automatically provisions a **Passthrough Network Load Balancer** when `service.type: LoadBalancer` is set on GKE. No manual load balancer setup is required.

# Prepare your initial configuration

1. First create the `sc4s` namespace that the rest of the resources will be deployed into:

```bash
kubectl create namespace sc4s
```

2. Add the SC4S Helm repository:

```bash
helm repo add splunk-connect-for-syslog https://splunk.github.io/splunk-connect-for-syslog
helm repo update
```

3. Create a `values.yaml` file with the following GCP-specific configuration:

```yaml
replicaCount: 2

splunk:
  hec_url: "https://<your-splunk-host>:8088"
  hec_token: "<your-hec-token>"
  hec_verify_tls: "yes"

image:
  repository: ghcr.io/splunk/splunk-connect-for-syslog/container3
  pullPolicy: IfNotPresent
  tag: ""

service:
  type: LoadBalancer
  usemetallb: false
  externalTrafficPolicy: Local

persistence:
  enabled: true
  size: "10Gi"

resources:
  requests:
    cpu: "1000m"
    memory: "512Mi"
  limits:
    cpu: "2000m"
    memory: "2Gi"

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 50
```

4. Add firewall rules to allow inbound syslog traffic:

```bash
gcloud compute firewall-rules create allow-sc4s-tcp \
  --network=default \
  --allow=tcp:514,tcp:601,tcp:6514 \
  --source-ranges=<your-syslog-sender-ip-ranges>

gcloud compute firewall-rules create allow-sc4s-udp \
  --network=default \
  --allow=udp:514 \
  --source-ranges=<your-syslog-sender-ip-ranges>
```

!!! warning
    GCP blocks all inbound traffic by default. These firewall rules are required for syslog traffic to reach SC4S. Replace `<your-syslog-sender-ip-ranges>` with the actual IP ranges of your syslog senders in CIDR notation (e.g. `10.0.0.0/8`). Avoid using `0.0.0.0/0` in production as it opens the ports to the entire internet.

# Deploy SC4S with your configuration

1. Install SC4S using the Helm chart:

```bash
helm install sc4s splunk-connect-for-syslog/splunk-connect-for-syslog \
  -f values.yaml \
  -n sc4s
```

2. Check that pods are running:

```bash
kubectl get pods -n sc4s
```

3. Get the external IP addresses assigned by GCP:

```bash
kubectl get services -n sc4s
```

You should see two `LoadBalancer` services with external IPs assigned — one for TCP and one for UDP. GCP provisions these automatically.

4. Check the logs to confirm SC4S started successfully:

```bash
kubectl logs {your_pod_name} -n sc4s
```

You should see something like this:

```ini
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=3.42.1
Configuring the health check port to: 8080
starting syslog-ng
```

If a pod does not start, debug it with:

```bash
kubectl describe pod {your_pod_name} -n sc4s
```

# Configure HPA (Horizontal Pod Autoscaler)

HPA is already enabled in the `values.yaml` above. Verify it is active after deployment:

```bash
kubectl get hpa -n sc4s
```

You should see `cpu: 1%/50%` with `MINPODS: 2` and `MAXPODS: 10`.

## Enable GKE Node Autoscaler (Required)

The SC4S Helm chart enforces **hard pod anti-affinity** — each SC4S pod must run on its own dedicated node. This prevents CPU saturation caused by multiple SC4S pods sharing a node, which would cause new pods to crash-loop during scale-up.

Because of this, when HPA requests more pods than there are available nodes, the new pods stay in `Pending` state. The GKE Node Autoscaler detects `Pending` pods and automatically adds new nodes to the cluster — allowing the pods to start cleanly.

!!! warning
    Without the Node Autoscaler enabled, new pods will stay `Pending` indefinitely when all nodes are occupied — HPA cannot scale beyond the initial node count. Previously, without hard pod anti-affinity, new pods were scheduled on already-saturated nodes and entered `CrashLoopBackOff` because syslog-ng could not initialize under CPU contention. Hard anti-affinity (built into the chart) prevents this by blocking co-location, but requires the Node Autoscaler to provide new nodes on demand.

Enable the Node Autoscaler with the following example:

```bash
gcloud container clusters update <your-cluster-name> \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5 \
  --region=<your-region> \
  --node-pool=default-pool
```

Refer to the [GKE cluster autoscaler documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler) for more details.

**How HPA + Node Autoscaler work together:**

1. Traffic increases → CPU rises above 50% threshold
2. HPA requests more SC4S pods
3. Hard anti-affinity blocks scheduling on existing nodes → pods go `Pending`
4. Node Autoscaler detects `Pending` pods → adds a new node
5. Pod schedules on the new dedicated node → starts cleanly
6. Traffic decreases → HPA scales pods back down → Node Autoscaler removes unused nodes

# Validate your configuration

SC4S performs checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng configuration is correct. Once the checks are complete, validate that SC4S properly communicates with Splunk. To do this, execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

# Update SC4S

Whenever the image is upgraded or when you want your configuration changes to be applied, run:

```bash
helm upgrade sc4s splunk-connect-for-syslog/splunk-connect-for-syslog \
  -f values.yaml \
  -n sc4s
```

# Stop SC4S

To delete the deployment run:

```bash
helm uninstall sc4s -n sc4s
```

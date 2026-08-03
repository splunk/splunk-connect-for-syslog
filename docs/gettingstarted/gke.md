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
  hec_url: "https://<your-splunk-host>:8088/services/collector/event"
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
  enabled: false
```


4. Add firewall rules to allow inbound syslog traffic:

```bash
gcloud compute firewall-rules create allow-sc4s-tcp \
  --network=default \
  --allow=tcp:514,tcp:601,tcp:6514 \
  --source-ranges=<your-syslog-sender-ip-ranges>

gcloud compute firewall-rules create allow-sc4s-udp \
  --network=default \
  --allow=udp:514,udp:601 \
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

The SC4S Helm chart's built-in HPA template uses the deprecated `autoscaling/v2beta1` API which was removed in Kubernetes 1.26. Since all GKE clusters run Kubernetes 1.26 or later, you must create the HPA manually using `autoscaling/v2`.

Refer to the [Kubernetes HPA documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) for background.

1. Create an `hpa.yaml` file:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: sc4s-autoscaler
  namespace: sc4s
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: sc4s-splunk-connect-for-syslog
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 30
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 10
      policies:
      - type: Percent
        value: 80
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max
```

2. Apply the HPA:

```bash
kubectl apply -f hpa.yaml
```

3. Verify the HPA is active:

```bash
kubectl get hpa -n sc4s
```

You should see `cpu: 1%/50%` with `MINPODS: 2` and `MAXPODS: 10`.

!!! note
    HPA scales pods horizontally (adds/removes pod instances) based on CPU usage. To allow new pods to start on new nodes when existing nodes are full, enable the [GKE cluster autoscaler](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler) which automatically adds nodes when pods cannot be scheduled.

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

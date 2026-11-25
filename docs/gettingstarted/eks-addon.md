You can install SC4S on Amazon EKS as an add-on from AWS Marketplace. EKS installs, configures and upgrades
SC4S for you, from the EKS console, the AWS CLI or infrastructure as code, so you don't run Helm yourself.

The add-on runs SC4S as a DaemonSet (one SC4S pod on each eligible node) behind internal Network Load Balancers,
and sends events to Splunk through the HTTP Event Collector (HEC).

| | |
|---|---|
| Add-on name | `splunk_splunk-connect-for-syslog` |
| Namespace | `sc4s` |
| Kubernetes versions | 1.31 - 1.37 |
| Architectures | amd64 and arm64 (AWS Graviton) |

To deploy SC4S on EKS yourself instead, see [EKS](eks.md).

# Before you begin

1. An EKS cluster, and `kubectl` and the AWS CLI configured for it.
2. Load balancer support, one of:
    - The [AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html)
      installed in the cluster.
    - [EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html). Set
      `service.loadBalancerClass: eks.amazonaws.com/nlb` when you install the add-on (see
      [Load balancer and networking](#load-balancer-and-networking)).
3. A Splunk HEC endpoint that the cluster can reach, and a HEC token. See [Splunk setup](getting-started-splunk-setup.md)
   for the indexes SC4S uses.
4. A subscription to Splunk Connect for Syslog in AWS Marketplace. You can subscribe from the EKS console while
   adding the add-on (step 2 below).

# Install the add-on

1. Create the namespace and a Secret with your HEC token. The add-on doesn't accept the token in its settings,
   so it must exist before you install:

    ```bash
    kubectl create namespace sc4s
    kubectl -n sc4s create secret generic sc4s-hec --from-literal=hec_token=<your-HEC-token>
    ```

    !!! warning "No trailing newline"
        Use `--from-literal`. If you use `--from-file`, make sure the file doesn't end with a newline, for example
        by writing it with `printf '%s' "$TOKEN" > token.txt`. A trailing newline ends up in the HEC
        `Authorization` header, and Splunk rejects the events.

2. Subscribe to the add-on. In the EKS console, open your cluster, then **Add-ons** > **Get more add-ons**. Under
   **AWS Marketplace add-ons**, select **Splunk Connect for Syslog** and follow the subscription link, then accept
   the terms. The subscription can take a few minutes to become active.

3. Create a settings file, for example `settings.yaml`. The minimum is the HEC URL and the Secret name:

    ```yaml
    splunk:
      hecUrl: https://splunk.example.com:8088
      existingSecret: sc4s-hec
    ```

    See [Configuration](#configuration) for all settings.

4. Install the add-on. In the console, finish the **Get more add-ons** flow and paste the settings under
   **Optional configuration settings**. With the AWS CLI:

    ```bash
    aws eks describe-addon-versions --addon-name splunk_splunk-connect-for-syslog \
      --query 'addons[].addonVersions[].addonVersion'
    aws eks create-addon --cluster-name <cluster> --addon-name splunk_splunk-connect-for-syslog \
      --addon-version <version> --configuration-values file://settings.yaml
    aws eks wait addon-active --cluster-name <cluster> --addon-name splunk_splunk-connect-for-syslog
    ```

    EKS validates the settings before it installs anything, and rejects unknown or misspelled settings.

# Validate the installation

1. Check the add-on status and the pods:

    ```bash
    aws eks describe-addon --cluster-name <cluster> --addon-name splunk_splunk-connect-for-syslog \
      --query 'addon.{status:status,health:health}'
    kubectl -n sc4s get daemonset,pods -o wide
    ```

    You should see one SC4S pod on each eligible node.

2. Check the startup checks in the logs. The label selector shows all pods. `kubectl logs ds/...` would show only one of them:

    ```bash
    kubectl -n sc4s logs -l app.kubernetes.io/name=splunk-connect-for-syslog --prefix --tail=50
    ```

    You should see:

    ```ini
    SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
    SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
    starting syslog-ng
    ```

3. Search Splunk for the SC4S startup event:

    ```ini
    index=* sourcetype=sc4s:events "starting up"
    ```

# Send syslog to SC4S

The add-on creates two Services, one for TCP and one for UDP, each backed by an internal Network Load Balancer.
Get their DNS names:

```bash
kubectl -n sc4s get svc
```

The `EXTERNAL-IP` column shows the NLB DNS names after a minute or two. Point your devices at them:

| Protocol | Ports |
|---|---|
| UDP | 514 (RFC 3164 and RFC 5424), 601 (RFC 5426) |
| TCP | 514, 601 (RFC 6587) |
| TLS | 6514, 5425 (RFC 5425). Only when TLS is configured; see [TLS listeners](#tls-listeners). |
| Vendor-specific ports | As set in `sc4s.vendorProduct` |

To test from inside the VPC:

```bash
echo "<134>$(date '+%b %d %H:%M:%S') testhost sc4s-test: hello over TCP" | nc -w2 <tcp-nlb-dns-name> 514
echo "<134>$(date '+%b %d %H:%M:%S') testhost sc4s-test: hello over UDP" | nc -u -w1 <udp-nlb-dns-name> 514
```

The events arrive in Splunk with `host=testhost`, as `sourcetype=sc4s:fallback`, because they match no vendor parser.

# Configuration

Settings are YAML or JSON. Pass them with `--configuration-values` or in the console. Only the settings below
are accepted. Use camelCase names; the Helm chart's older snake_case names (such as `hec_url`) are rejected.

| Setting | Purpose |
|---|---|
| `splunk.hecUrl` | HEC URL, for example `https://splunk.example.com:8088`. Separate multiple URLs with commas. |
| `splunk.existingSecret`, `splunk.existingSecretKey` | Secret and key holding the HEC token. Default `sc4s-hec` and `hec_token`. |
| `splunk.hecVerifyTls` | Verify the HEC certificate, `"yes"` (default) or `"no"`. |
| `splunk.hecTls` | Secret with a client certificate for HEC (mutual TLS), keys `cert.pem` and `key.pem`. |
| `sc4s.vendorProduct` | Dedicated listener ports per vendor and product. |
| `sc4s.contextFiles` | Context files such as `splunk_metadata.csv` and `host.csv`. |
| `sc4s.configFiles` | Custom parsers (`app_parsers`). |
| `sc4s.addons` | Add-on selection (`config.yaml`). |
| `sc4s.existingCert` | TLS Secret for the TLS syslog listeners. |
| `sc4s.proxy.http`, `.https`, `.noProxy` | HTTP proxy for HEC traffic. |
| `sc4s.listenPorts.*` | Container ports of the default listeners. The Services always expose the standard ports. |
| `env` | Any other SC4S setting. See [SC4S configuration variables](../configuration.md). Settings the add-on manages, and names that look like credentials, are rejected. |
| `service.*` | `annotations`, `loadBalancerClass`, `loadBalancerSourceRanges`, `loadBalancerIP`, `externalTrafficPolicy`, `type` |
| `persistence.enabled`, `.size`, `.hostPath` | The disk buffer. See [Disk buffer](#disk-buffer). |
| `resources`, `nodeSelector`, `tolerations`, `podAnnotations` | Sizing and scheduling. |

A fuller example:

```yaml
splunk:
  hecUrl: https://splunk.example.com:8088
  existingSecret: sc4s-hec
service:
  loadBalancerSourceRanges:          # networks allowed to send syslog
    - 10.0.0.0/8
sc4s:
  vendorProduct:
    - name: checkpoint
      ports:
        tcp: [9000]
        udp: [9000]
  contextFiles:
    splunk_metadata.csv: |-
      cisco_asa,index,netfw
env:
  SC4S_SOURCE_LISTEN_UDP_SOCKETS: "4"
```

To change settings later, edit them in the console, or run `aws eks update-addon` with `--configuration-values`.
The value replaces your previous settings entirely, so always pass the complete settings.
Most changes restart the SC4S pods one node at a time, so each pod is briefly unavailable. Changes that only
affect the Services, such as `loadBalancerSourceRanges`, don't restart the pods.

## Metadata, vendor ports and custom parsers

The `sc4s` settings map to the usual SC4S configuration:
- `contextFiles` overrides index, sourcetype and other metadata. See [Configure SC4S metadata](../configuration.md#configure-sc4s-metadata).
- `vendorProduct` opens dedicated ports. See [Syslog source configuration](../configuration.md#syslog-source-configuration).
- `configFiles` adds custom parsers.

The [MicroK8s guide](k8s-microk8s.md) explains these blocks in more detail. It uses the Helm chart that the add-on
is built from, but with the older names: `vendor_product`, `context_files` and `config_files` are `vendorProduct`,
`contextFiles` and `configFiles` in the add-on.

## TLS listeners

Create a `kubernetes.io/tls` Secret with the certificate and key that SC4S presents to senders, and set
`sc4s.existingCert`:

```bash
kubectl -n sc4s create secret tls sc4s-tls --cert=server.crt --key=server.key
```

```yaml
sc4s:
  existingCert: sc4s-tls
```

This enables the TLS listeners on 6514 and 5425. SC4S doesn't ask senders for client certificates. Without
`existingCert`, nothing listens on the TLS ports.

## HEC certificates

By default, SC4S verifies the HEC certificate against the public CAs in its image. That works for Splunk Cloud
Platform. A private CA isn't currently supported with the add-on, because SC4S runs as a non-root user and can't add
it to the system trust store. If your HEC endpoint uses a private CA, set `splunk.hecVerifyTls: "no"`.

# Load balancer and networking

By default the add-on creates internal NLBs that send traffic directly to the pod IPs (target type `ip`), with a
health check on HTTP port 8080, path `/health`. Your entries under `service.annotations` are added to these
defaults, and an entry with the same name replaces the default.

- **EKS Auto Mode:** set `service.loadBalancerClass: eks.amazonaws.com/nlb` at install time. It can't be changed
  later without recreating the Services, and so the NLBs.
- **Subnets:** if the controller can't choose subnets (the NLB stays `<pending>`), name them:
  `service.beta.kubernetes.io/aws-load-balancer-subnets: subnet-aaa,subnet-bbb`.
- **Who can send:** syslog has no authentication. Restrict senders with `service.loadBalancerSourceRanges` and
  security groups. Keep the NLBs internal unless you need otherwise.
- **Source IP:** SC4S uses the sender's IP for events without a hostname, for `host.csv` and for source-based
  routing. UDP keeps the source IP. For TCP and TLS, turn on client IP preservation by replacing the
  target group attributes:

    ```yaml
    service:
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-target-group-attributes: "stickiness.enabled=false,deregistration_delay.timeout_seconds=300,deregistration_delay.connection_termination.enabled=false,preserve_client_ip.enabled=true"
    ```

    With client IP preservation on, the pods' security groups must allow the senders' addresses.
- **Stable addresses:** the NLBs belong to the add-on's Services. Deleting the add-on deletes them, and a new install
  gets new DNS names and IP addresses. If your devices are configured with IP addresses, keep the add-on installed
  and change it with `update-addon`, or pin the NLB's private IPs with the
  `service.beta.kubernetes.io/aws-load-balancer-private-ipv4-addresses` annotation.

For more on running SC4S behind an NLB, see [AWS Network Load Balancer](../architecture/lb/nlb.md).

# Sizing and performance

- **One pod per node.** SC4S scales with the number of nodes it runs on. Run it on dedicated nodes: label and taint
  a node group, then set `nodeSelector` and `tolerations`. Otherwise every node in the cluster runs an SC4S pod.

    ```yaml
    nodeSelector:
      role: sc4s
    tolerations:
      - key: dedicated
        value: sc4s
        effect: NoSchedule
    ```

- **Resources.** Each pod requests 1 CPU and 1 GiB by default, with no limits, so SC4S can use the whole node. Avoid
  CPU limits: throttling causes UDP loss. Throughput depends mostly on the node's size.
- **No autoscaling.** To scale, resize the dedicated node group. Each connection, and each UDP sender address and
  port, stays on one pod, so new nodes only receive new connections, and a single busy sender is limited to one pod.
- **High-volume UDP.** Raise `net.core.rmem_max` on the nodes (for example in the node group's launch template)
  and set `env.SC4S_SOURCE_UDP_SO_RCVBUFF`. With default buffers, UDP loses events at high rates. See
  [Tune the receiving buffer](../architecture/fine-tuning.md#tune-the-receiving-buffer).

# Disk buffer

SC4S queues events on disk while HEC is unavailable. With the add-on, the buffer is a directory on each node,
`/var/lib/sc4s/sc4s/<release>`, capped at `persistence.size` (default `10Gi`).
- The buffer survives pod restarts and upgrades.
- It's lost if the node is removed, for example by scaling in, node replacement or Spot interruption.
- It isn't deleted when you remove the add-on.
- The buffer uses a hostPath volume, which the `baseline` and `restricted` Pod Security Standards don't allow.
  On clusters that enforce them, set `persistence.enabled: false`. Queued events are then kept in memory only.

For more, see [Configure your SC4S disk buffer](../configuration.md#configure-your-sc4s-disk-buffer).

# Upgrade and remove

EKS doesn't upgrade add-ons automatically. To upgrade:

```bash
aws eks describe-addon-versions --kubernetes-version <cluster-version> --addon-name splunk_splunk-connect-for-syslog \
  --query 'addons[].addonVersions[].addonVersion'
aws eks update-addon --cluster-name <cluster> --addon-name splunk_splunk-connect-for-syslog --addon-version <version>
```

Leave out `--configuration-values` to keep your current settings. Pods are replaced one node at a time, and the
events queued in each node's buffer are kept.

To remove the add-on:

```bash
aws eks delete-addon --cluster-name <cluster> --addon-name splunk_splunk-connect-for-syslog
```

Removing the add-on deletes the NLBs. The HEC token Secret and the buffer directories on the nodes stay; delete
them yourself.

# Troubleshooting

| Symptom | What to check |
|---|---|
| Add-on status `CREATE_FAILED` with `AddonSubscriptionNeeded` | Subscribe in AWS Marketplace, then remove the add-on and install it again. |
| Settings rejected when installing or updating | The message names the setting. Check it against [Configuration](#configuration); names are camelCase. |
| Pods in `CreateContainerConfigError` | The HEC token Secret is missing, or has a different name or key. |
| `EXTERNAL-IP` stays `<pending>` | No load balancer controller, or no usable subnets. Check `kubectl -n kube-system logs deploy/aws-load-balancer-controller`, or set the subnets annotation. On Auto Mode, set `loadBalancerClass`. |
| No events in Splunk | Check the `SC4S_ENV_CHECK_HEC` lines in the logs, the HEC URL and token, and that the indexes exist. |
| TLS or connection errors you can't see | syslog-ng's own messages go to Splunk as `sourcetype=sc4s:events`, not to the pod log. To see them in the pod log, set `env.SC4S_DEBUG_LOGS: "yes"`. It's very verbose, so use it for troubleshooting only. |

For more, see [Troubleshooting](../troubleshooting/troubleshoot_resources.md).

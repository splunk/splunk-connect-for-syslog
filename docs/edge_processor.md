# Edge Processor integration guide (Experimental)

## Intro

You can use the `Edge Processor` to:

* Enrich log messages with extra data, such as adding a new field or overriding an index using `SPL2`.
* Filter log messages using `SPL2`.
* Send log messages to alternative destinations, for example, `AWS S3` or `Apache Kafka`.

## How it works

```mermaid
stateDiagram
    direction LR

    SC4S: SC4S
    EP: Edge Processor
    Dest: Another destination
    Device: Your device
    S3: AWS S3
    Instance: Instance
    Pipeline: Pipeline with SPL2

    Device --> SC4S: Syslog protocol
    SC4S --> EP: HEC
    state EP {
      direction LR
      Instance --> Pipeline
    }
    EP --> Splunk
    EP --> S3
    EP --> Dest
```

## Set up the Edge Processor for SC4S

SC4S [using same protocol](https://docs.splunk.com/Documentation/SplunkCloud/latest/EdgeProcessor/HECSource) for communication with Splunk and Edge Processor. For that reason setup process will be very similar, but it have some differences.

/// tab | Set up on Docker / Podman
1. On the `env_file`, configure the HEC URL as IP of *managed instance*, that you registered on Edge Processor.
2. Add your HEC token. You can find your token in the Edge Processor "global settings" page. 

```
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=http://x.x.x.x:8088
SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=no
```
///

/// tab | Set up on Kubernetes
1. Set up the Edge Processor on your `values.yaml` HEC URL using the IP of *managed instance*, that you registered on Edge Processor.
2. Provide the hec_token. You can find this token on the Edge Processor's "global settings" page.

```
splunk:
  hec_url: "http://x.x.x.x:8088"
  hec_token: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  hec_verify_tls: "no"
```
///

## mTLS encryption

Before setup, [generate mTLS certificates](https://docs.splunk.com/Documentation/SplunkCloud/latest/EdgeProcessor/SecureForwarders). Server mTLS certificates should be uploaded to `Edge Processor` and client certifcates should be used with `SC4S`.

**Rename the certificate files. SC4S requires the following names**:

  * `key.pem` - client certificate key
  * `cert.pem` - client certificate
  * `ca_cert.pem` - certificate authority

/// tab | Set up on Docker / Podman
1. Use HTTPS in HEC url: `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://x.x.x.x:8088`.
2. Move your clients mTLS certificates (`key.pem`, `cert.pem`, `ca_cert.pem`) to `/opt/sc4s/tls/hec`.
3. Mount `/opt/sc4s/tls/hec` to `/etc/syslog-ng/tls/hec` using docker/podman volumes.
4. Define mounting mTLS point for HEC: `SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_MOUNT=/etc/syslog-ng/tls/hec`.
5. Start or restart SC4S.
///

/// tab | Set up on Kubernetes
1. Add the secret name of the mTLS certificates to the `values.yaml` file:

```
splunk:
  hec_url: "https://x.x.x.x:8088"
  hec_token: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  hec_tls: "hec-tls-secret"
```

2. Add your mTLS certificates to the `charts/splunk-connect-for-syslog/secrets.yaml` file:

```
hec_tls:
  secret: "hec-tls-secret"
  value:
    key: |
      -----BEGIN PRIVATE KEY-----
      Exmaple key
      -----END PRIVATE KEY-----
    cert: |
      -----BEGIN CERTIFICATE-----
      Exmaple cert
      -----END CERTIFICATE-----
    ca: |
      -----BEGIN CERTIFICATE-----
      Example ca
      -----END CERTIFICATE-----
```

3. Encrypt your `secrets.yaml`:

```
ansible-vault encrypt charts/splunk-connect-for-syslog/secrets.yaml
```

4. Add the IP address for your cluster nodes to the inventory file `ansible/inventory/inventory_microk8s_ha.yaml`.

5. Deploy the Ansible playbook:

```
ansible-playbook -i ansible/inventory/inventory_microk8s_ha.yaml ansible/playbooks/microk8s_ha.yml --ask-vault-pass
```
///

## Scaling Edge Processor

To scale you can distribute traffic between Edge Processor **managed instances**. To set this up, update the HEC URL with a comma-separated list of URLs for your managed instances.

/// tab | Set up on Docker/Podman
Update HEC URL in `env_file`:

```
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=http://x.x.x.x:8088,http://x.x.x.x:8088,http://x.x.x.x:8088
```
///

/// tab | Set up on Kubernetes
Update HEC URL in `values.yaml`:

```
splunk:
  hec_url: "http://x.x.x.x:8088,http://x.x.x.x:8088,http://x.x.x.x:8088"
```
///

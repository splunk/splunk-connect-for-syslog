# Edge Processor integration guide

## Intro

`Edge Processor` can be used on that usecases:

* Enrich log message extra data (for example add some field or override index) using `SPL2`
* Filter log message using `SPL2`
* Send log messages to alternative destanations (like `AWS S3`, `Apache Kafka`, etc.)

## How it's working

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

## Basic Setup

### Docker / Podman

Setup on your `env_file` HEC URL as IP of EP worker EC2 instance.
Token you can find in EP "global settings" page.

```
SC4S_DEST_SPLUNK_HEC_{EP1}_URL=http://x.x.x.x:8088
SC4S_DEST_SPLUNK_HEC_{EP1}_TOKEN=secret
```

### Kubernetes

Setup on your `values.yaml` HEC URL as IP of EP worker EC2 instance.
Token you can find in EP "global settings"page.

```
splunk:
  hec_url: "https://x.x.x.x:8088"
  hec_token: "secret"
```

## mTLS encryption

### Preparing certs

Before setup you need to [generate mTLS certificates](https://docs.splunk.com/Documentation/SplunkCloud/9.1.2308/EdgeProcessor/SecureForwarders). Server mTLS certificates should be uploaded to `Edge Processor` and client certifcates should be used with `SC4S`.

Please rename your files, we expcting such filenames for client mTLS cerificates:

  * `key.pem` - client certificate key
  * `cert.pem` - client certificate
  * `ca_cert.pem` - certificate authority

### Docker / Podman

  1. Use HTTPS in HEC url: `SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=https://x.x.x.x:8088`
  2. Move your clients mTLS certificates to `/opt/sc4s/tls/hec`
  3. Mount `/opt/sc4s/tls/hec` to `/etc/syslog-ng/tls/hec` using docker/podman volumes.
  4. Define mounting mTLS point for HEC: `SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_MOUNT=/etc/syslog-ng/tls/hec`
  5. Start/Restart SC4S

### Kubernetes

  1. Add secret name of mTLS certs at `values.yaml`:

```
splunk:
  hec_url: "https://x.x.x.x:8088"
  hec_token: "secret"
  hec_tls: "secret-name"
```

  2. Add your mtls certs at `secrets.yaml`:

```
hec_tls:
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

  3. Encrypt your `secrets.yaml` using `ansible-vault`.
  4. Add IP of cluster nodes to inventory file `ansible/inventory/inventory_microk8s_ha.yaml`
  5. Deploy ansible playbook `ansible/playbooks/microk8s_ha.yml`
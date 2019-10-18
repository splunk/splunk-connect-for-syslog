
This deployment method has one specific restriction the same external port can not be used for both TCP AND UDP
For example normally port 515 is listening on both tcp and udp. In this deployment k8s does not allow both protocols

Port 514 will be UDP only (most common) and port 1514 will be TCP


## Install the k3s distro of k8s

```bash
curl -sfL https://get.k3s.io | sh -
```

## Install the openebs storage provider

This provider will be used to protect the on disk queue between restarts for sc4s by default the path used is ``/var/openebs/local``

```bash
kubectl apply -f https://openebs.github.io/charts/openebs-operator-1.3.0.yaml
```

## Verify k3s

Check the version

```bash
sudo /usr/local/bin/kubectl version
```

Should be at lease 1.15 for client and server

```text
Client Version: version.Info{Major:"1", Minor:"15", GitVersion:"v1.15.4-k3s.1", GitCommit:"a7531b1ab3fd5ff987b074472ddfb84a2f5326bc", GitTreeState:"clean", BuildDate:"2019-09-19T22:36Z", GoVersion:"go1.12.9", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"15", GitVersion:"v1.15.4-k3s.1", GitCommit:"a7531b1ab3fd5ff987b074472ddfb84a2f5326bc", GitTreeState:"clean", BuildDate:"2019-09-19T22:36Z", GoVersion:"go1.12.9", Compiler:"gc", Platform:"linux/amd64"}
```

## Create a namespace for sc4s

```bash
sudo /usr/local/bin/kubectl create ns sc4s
```

## Apply the manifest

save the contents of the yml file at the end of this doc into  a file named `sc4s.yaml`

```bash
sudo /usr/local/bin/kubectl -n sc4s apply -f sc4s.yaml 
```

## Listen on additional ports

* Update the ``sc4s.yaml`` file config map to include the additional port required from sources.md use the apply command above

* create a new file ``sc4s-vendor_product.yaml`` where vendor product matches the port in use using the following template

```yaml
# Notes the due to k8s restrictions the UDP and TCP listeners can not be on the same port
# We will use 5000 series ports for udp and 6000 series ports for tcp
# The target port for both will match the 5000 series port
apiVersion: v1
kind: Service
metadata:
  name: sc4s-vendor-product-tcp
  labels:
    app: sc4s
spec:
  type: LoadBalancer
  ports:
  - port: 6000
    targetPort: 5000
    protocol: TCP
    name: syslog-vendor-product-tcp
  selector:
    app: sc4s
---
apiVersion: v1
kind: Service
metadata:
  name: sc4s-vendor-product-udp
  labels:
    app: sc4s
spec:
  type: LoadBalancer
  ports:
  - port: 5000
    targetPort: 5000
    protocol: UDP
    name: syslog-vendor-product-udp
  selector:
    app: sc4s
``` 

## Apply config changes

After updating the sc4s.yaml file as needed and issuing the apply command above use the following
to initiate a deployment
```bash
sudo /usr/local/bin/kubectl -n sc4s rollout restart deploy/sc4s-deployment
```

## sc4s.yaml


```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sc4s-env
data:
  SPLUNK_HEC_URL: "https://splunk.smg.aws:8088/services/collector/event"
  SPLUNK_HEC_TOKEN: "a778f63a-5dff-4e3c-a72c-a03183659e94"
  SC4S_DEST_SPLUNK_HEC_WORKERS: "6"
  SPLUNK_CONNECT_METHOD: "hec"
  SPLUNK_DEFAULT_INDEX: "main"
  SPLUNK_METRICS_INDEX: "em_metrics"
  SC4S_DEST_SPLUNK_HEC_TLS_VERIFY: "no"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: sc4s-config
data:
  compliance_meta_by_source.conf: |
    @version: 3.24
    #filter f_test_test {
    #    host("something-*" type(glob)) or
    #    netmask(192.168.100.1/24)
    #};

  compliance_meta_by_source.csv: |
    #f_test_test,.splunk.index,"badindex"
    #f_test_test,fields.compliance,"pci"

  vendor_product_by_source.csv: |
    f_test_test,sc4s_vendor_product,"test_test"
    f_cisco_meraki,sc4s_vendor_product,"cisco_meraki"
    f_juniper_nsm,sc4s_vendor_product,"juniper_nsm"
    f_juniper_nsm_idp,sc4s_vendor_product,"juniper_nsm_idp"
    f_juniper_idp,sc4s_vendor_product,"juniper_idp"
    f_juniper_netscreen,sc4s_vendor_product,"juniper_netscreen"
    f_cisco_nx_os,sc4s_vendor_product,"cisco_nx_os"
    f_proofpoint_pps_sendmail,sc4s_vendor_product,"proofpoint_pps_sendmail"
    f_proofpoint_pps_filter,sc4s_vendor_product,"proofpoint_pps_filter"
  vendor_product_by_source.conf: |
    @version: 3.24

    filter f_test_test {
        host("testvp-*" type(glob)) or
        netmask(192.168.100.1/24)
    };
    filter f_juniper_idp {
        host("jnpidp-*" type(glob)) or
        netmask(192.168.3.0/24)
    };
    filter f_juniper_netscreen {
        host("jnpns-*" type(glob)) or
        netmask(192.168.4.0/24)
    };
    filter f_juniper_nsm {
        host("jnpnsm-*" type(glob)) or
        netmask(192.168.1.0/24)
    };
    filter f_juniper_nsm_idp {
        host("jnpnsmidp-*" type(glob)) or
        netmask(192.168.2.0/24)
    };
    filter f_cisco_meraki {
        host("testcm-*" type(glob)) or
        netmask(192.168.4.0/24)
    };
    filter f_cisco_nx_os {
        host("csconx-*" type(glob)) or
        netmask(192.168.5.0/24)
    };
    filter f_proofpoint_pps_filter {
        host("pps-*" type(glob)) or
        netmask(192.168.7.0/24)
    };
    filter f_proofpoint_pps_sendmail {
        host("pps-*" type(glob)) or
        netmask(192.168.6.0/24)
    };
  
  splunk_index.csv: |
    #bluecoat_proxy,index,netproxy
    #cef_ArcSight_ArcSight,index,netwaf
    #cef_Incapsula_SIEMintegration,index,netwaf
    #cef_Microsoft_Microsoft Windows,index,oswinsec
    #cef_Microsoft_System or Application Event,index,oswin
    #checkpoint_splunk,index,netops
    #checkpoint_splunk_dlp,index,netdlp
    #checkpoint_splunk_email,index,email
    #checkpoint_splunk_firewall,index,netfw
    #checkpoint_splunk_sessions,index,netops
    #checkpoint_splunk_web,index,netproxy
    #checkpoint_splunk,index,netops
    #checkpoint_splunk,index,netops
    #cisco_asa,index,netfw
    #cisco_ios,index,netops
    #cisco_nx_os,index,netops
    #local_example,index,main
    #forcepoint_webprotect,index,netproxy
    #fortinet_fortios_event,index,netops
    #fortinet_fortios_log,index,netops
    #fortinet_fortios_traffic,index,netfw
    #fortinet_fortios_utm,index,netids
    #juniper_idp,index,netids
    #juniper_structured,index,netops
    #juniper_idp_structured,index,netids
    #juniper_junos_fw_structured,index,netfw
    #juniper_junos_ids_structured,index,netids
    #juniper_junos_utm_structured,index,netfw
    #juniper_junos_fw,index,netfw
    #juniper_junos_ids,index,netids
    #juniper_junos_utm,index,netfw
    #juniper_sslvpn,index,netfw
    #juniper_netscreen,index,netfw
    #juniper_nsm,index,netfw
    #juniper_nsm_idp,index,netids
    #juniper_legacy,index,netops
    #pan_traffic,index,netfw
    #pan_threat,index,netproxy
    #pan_system,index,netops
    #pan_config,index,netops
    #pan_hipwatch,index,main
    #pan_correlation,index,main
    #pan_userid,index,netauth
    #pan_unknown,index,netops
    #proofpoint_pps_filter,index,email
    #proofpoint_pps_sendmail,index,email
    #sc4s_events,index,main
    #sc4s_fallback,index,main
    #sc4s_metrics,index,em_metrics


---
apiVersion: v1
kind: Service
metadata:
  name: sc4s-tcp
  labels:
    app: sc4s
spec:
  type: LoadBalancer
  ports:
  - port: 515
    targetPort: 514
    protocol: TCP
    name: syslog-tcp
  selector:
    app: sc4s
---
apiVersion: v1
kind: Service
metadata:
  name: sc4s-udp
  labels:
    app: sc4s
spec:
  type: LoadBalancer
  ports:
  - port: 514
    targetPort: 514
    protocol: UDP
    name: syslog-udp
  selector:
    app: sc4s
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: sc4s-pv-claim
  labels:
    app: sc4s
spec:
  storageClassName: openebs-hostpath
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
# The following will deploy the container
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sc4s-deployment
  labels:
    app: sc4s
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sc4s
  template:
    metadata:
      labels:
        app: sc4s
    spec:
      containers:
      - name: sc4s
        image: splunk/scs:1.0.2
        ports:
        - containerPort: 514
        - containerPort: 601
        envFrom:
        - configMapRef:
            name: sc4s-env
        volumeMounts:
        - name: config-volume
          mountPath: /opt/syslog-ng/etc/conf.d/local/context
        - name: queue-volume
          mountPath: /opt/syslog-ng/var/data/disk-buffer
      volumes:
        - name: config-volume
          configMap:
             name: sc4s-config
        - name: queue-volume
          persistentVolumeClaim:
            claimName: sc4s-pv-claim
```
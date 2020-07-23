
# Install MicroK8s - ALPHA

Use the following command in step 3 "Turn on the services you want"

```microk8s enable dns helm metallb rbac storage```
* Answer No to the following prompt "Enforce mutual TLS authentication"
* Enter a IP in the same range as the host not used by the host, this IP will be used as a shared or cluster IP if a second host is added for HA. This must be entered as a range even when only one IP is used.

Refer to relevant installation guides:

* [Linux](https://microk8s.io/docs)
* Windows and MacOSX are untested at this time

# Store the HEC token as a secret

* Replace the guid in the following block with the correct guid for your target Splunk endpoint

```bash
echo -n '1f9a6810-5b25-478b-b024-1097d656a046' > hec_token
kubectl create secret generic sc4s-secrets  --from-file=./hec_token
rm hec_token.txt
```

# Create a configmap with environment variables for sc4s

create the following file ```env_file```

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

```bash
kubectl create configmap sc4s-env-file --from-env-file=./env_file
```

# Create a configmap with context dagta for sc4s

kubectl apply -f sc4s-context.yaml

# Deploy SC4S

kubectl apply -f sc4s.yaml


# Change configuration

Note change change to the following config will trigger a restart of the container

```bash
kubectl edit configmap sc4s-env-file
kubectl edit configmap sc4s-context-config
```
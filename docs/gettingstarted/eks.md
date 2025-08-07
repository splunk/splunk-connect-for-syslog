You can install SC4S on AWS with EKS. To do this, you can use a deployment file and a basic configuration information.

Refer to AWS [documentation](https://docs.aws.amazon.com/eks/latest/userguide/sample-deployment.html) on how to set up your AWS environment. 

Before you begin you also need to have `kubectl` installed.

# Prepare your initial configuration
1. First create a file named `/opt/sc4s/env_file` and add the following environment variables and values:

``` dotenv
--8<---- "ansible/resources/env_file"
```
Then create a configmap with variables provided in the file
```
kubectl create configmap sc4s-config --from-env-file=/opt/sc4s/env_file -n sc4s
```

2. Create a deployment configuration file based on this:
``` yaml
--8<---- "docs/resources/docker/sc4s_deployment.yaml"
```

3. (Optioinal) To use local filters you have to load them into a configmap, and uncomment parts of the deployment file related to them:

```
kubectl create configmap sc4s-local-filter-config \                  
  --from-file=/opt/sc4s/local/config/app_parsers  -n sc4s
```

This loads files from app_parsers directory only, [here](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#create-configmaps-from-files) is the documentation explaining other use cases.

<!-- I think this is a clunky way of doing it, other option is to use InitContainer and preload them somewhere in AWS -->

# Deploy SC4S with your configuration
1. To run SC4S simply run this command in the directory where your deployment file is located:
```bash
kubectl apply -f sc4s_deployment.yaml
```

You can use a load balancer with SC4S, to set it up properly refer to our [documentation](../architecture/lb/index.md).

2. You can use following commands to check if SC4S deployment and NodePort service is running.

To get pods:
```bash
kubectl get pods -n sc4s
```

To get NodePort service:
```bash
kubectl get services -n sc4s
```

Check the logs using this command:
```bash
kubectl logs {your_pod_name} -n sc4s
```

You should see something like this:
```ini
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:fallback...
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=main for sourcetype=sc4s:events...
syslog-ng checking config
sc4s version=3.37.0
Configuring the health check port to: 8080
[2025-08-01 17:40:50 +0000] [130] [INFO] Starting gunicorn 23.0.0
[2025-08-01 17:40:50 +0000] [130] [INFO] Listening at: http://0.0.0.0:8080 (130)
[2025-08-01 17:40:50 +0000] [130] [INFO] Using worker: sync
[2025-08-01 17:40:50 +0000] [133] [INFO] Booting worker with pid: 133
starting syslog-ng
```

If the pod does not start you can debug it with this command:
```bash
kubectl describe pod {your_pod_name} -n sc4s
```

3. You can use following commands to check if SC4S deployment and NodePort service is running.


# Validate your configuration

SC4S performs checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct. Once the checks are complete, validate that SC4S properly communicate with Splunk.
To do this, execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```

# Update SC4S 
Whenever the image is upgraded or when you want your configuration changes to be applied, run the command:

```bash
kubectl apply -f sc4s_deployment.yaml
```

Kubectl will detect if there are any changes to be made and rollout new pods if necessary.

# Stop SC4S

To delete the deployment run this command in the directory where your deployment file is located:
```bash
kubectl delete -f sc4s_deployment.yaml
```

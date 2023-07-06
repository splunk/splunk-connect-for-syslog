#### Microk8s tests are not yet meant to be run in CICD, though can be run locally.
### To run mk8s tests locally:
#### Prerequisites:
  - running instance of Splunk configured for SC4S.
  - a host for running SC4S on mk8s (preferably Ubuntu 22.04).

1. In [inventory file](ansible/inventory/inventory_microk8s) add ip of your instance.
2. Copy contents of `tests/mk8s_tests/values.yaml`  to `charts/splunk-connect-for-syslog/values.yaml` and fill in hec url, token and tls verification. Fill in your machine IP at line 30 (if you are using VPN get it form `ifconfig`.). 
2. Spin up docker-compose with ansible installed and exec into it.
```bash
    docker-compose -f ansible/docker-compose.yml up   
    docker exec -it ansible_sc4s /bin/bash
```
3. Run ansible playbook:
``` bash 
ansible-playbook -i ansible/inventory/inventory.yaml -u splunker --ask-pass ansible/playbooks/microk8s.yml
```
4. Execute tests (either in docker or directly on your machine): 
```bash
 poetry run pytest -v \
   --tb=long             \
   --splunk_type=external     \        
   --splunk_hec_token=<<hec token>>     \
   --splunk_host=<<splunk host>>  \
   --splunk_password= <<splunk password>> \
   --sc4s_host=<<sc4s host>>  \
   --junitxml=test-results/test.xml        \      
   -n 4   $(ls tests/test_mk8s_*)
```
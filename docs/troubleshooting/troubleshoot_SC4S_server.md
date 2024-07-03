# Validate server startup and operations

This topic helps you find the most common solutions to startup and operational issues with SC4S. 

If you plan to run SC4S with standard configuration, we recommend that you perform startup out of systemd.  

If you are using a custom configuration of SC4S with significant modifications, for example, multiple unique ports for sources, hostname/CIDR block configuration for sources, or new log paths,  start SC4S with the container runtime command `podman` or `docker` directly from the command line as described in this topic.  When you are satisfied with the operation, you can then transition to systemd.

## Issue: systemd errors occur during SC4S startup 
If you are running out of systemd, you may see this at startup:

```bash
[root@sc4s syslog-ng]# systemctl start sc4s
Job for sc4s.service failed because the control process exited with error code. See "systemctl status sc4s.service" and "journalctl -xe" for details.
```
Most issues that occur with startup and operation of SC4S involve syntax errors or duplicate listening ports.

Try the following to resolve the issue:

### Check that your SC4S container is running
If you start with systemd and the container is not running, check with the following:
```
journalctl -b -u sc4s | tail -100
```
This will print the last 100 lines of the system journal in detail, which should be sufficient to see the specific syntax or runtime failure and guide you in troubleshooting the unexpected container exit.

### Check that the SC4S container starts and runs properly outside of the systemd service environment
As an alternative to launching with systemd during the initial installation phase, you can test the container startup outside of the systemd startup environment. This is especially important for troubleshooting or log path development, for example, when `SC4S_DEBUG_CONTAINER` is set to "yes". 

The following command launches the container directly from the command line. This command assumes the local mounted directories are set up as shown in the "getting started" examples. Adjust for your local requirements, if you are using Docker, substitute "docker" for "podman" for the container runtime command.

```bash
/usr/bin/podman run \
    -v splunk-sc4s-var:/var/lib/syslog-ng \
    -v /opt/sc4s/local:/etc/syslog-ng/conf.d/local:z \
    -v /opt/sc4s/archive:/var/lib/syslog-ng/archive:z \
    -v /opt/sc4s/tls:/etc/syslog-ng/tls:z \
    --env-file=/opt/sc4s/env_file \
    --network host \
    --name SC4S \
    --rm ghcr.io/splunk/splunk-connect-for-syslog/container3:latest
```


### Check that the container is still running when systemd indicates that it's not running

In some instances, particularly when `SC4S_DEBUG_CONTAINER=yes`, an SC4S container might not shut down completely when starting/stopping out of systemd, and systemd will attempt to start a new container when one is already running with the `SC4S` name. You will see this type of output when viewing the journal after a failed start caused by this condition, or a similar message when the container is run directly from the CLI:

```
Jul 15 18:45:20 sra-sc4s-alln01-02 podman[11187]: Error: error creating container storage: the container name "SC4S" is already in use by "894357502b2a7142d097ea3ca1468d1cb4fbc69959a9817a1bbe145a09d37fb9". You have to remove that container...
Jul 15 18:45:20 sra-sc4s-alln01-02 systemd[1]: sc4s.service: Main process exited, code=exited, status=125/n/a
```

To rectify this, execute:
```
podman rm -f SC4S
```

SC4S should then start normally.

Do not use systemd when `SC4S_DEBUG_CONTAINER` is set to "yes", instead use the CLI `podman` or `docker` commands directly to start/stop SC4S.

## Issue: HEC/token connection errors, for example, “No data in Splunk”

SC4S performs basic HEC connectivity and index checks at startup and creates logs that indicate general connection issues and indexes that may not be accessible or configured on Splunk. To check the container logs that contain the results of these tests, run:

```bash
/usr/bin/<podman|docker> logs SC4S
```

You will see entries similar to the following:

```
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful; checking indexes...

SC4S_ENV_CHECK_INDEX: Checking email {"text":"Incorrect index","code":7,"invalid-event-number":1}
SC4S_ENV_CHECK_INDEX: Checking epav {"text":"Incorrect index","code":7,"invalid-event-number":1}
SC4S_ENV_CHECK_INDEX: Checking main {"text":"Success","code":0}
```

Note the specifics of the indexes that are not configured correctly, and rectify this in your Splunk configuration. If this is not addressed properly, you may see output similar to the below when data flows into SC4S:

```
Mar 16 19:00:06 b817af4e89da syslog-ng[1]: Server returned with a 4XX (client errors) status code, which means we are not authorized or the URL is not found.; url='https://splunk-instance.com:8088/services/collector/event', status_code='400', driver='d_hec#0', location='/opt/syslog-ng/etc/conf.d/destinations/splunk_hec.conf:2:5'
Mar 16 19:00:06 b817af4e89da syslog-ng[1]: Server disconnected while preparing messages for sending, trying again; driver='d_hec#0', location='/opt/syslog-ng/etc/conf.d/destinations/splunk_hec.conf:2:5', worker_index='4', time_reopen='10', batch_size='1000'
```
This is an indication that the standard `d_hec` destination in syslog-ng, which is the route to Splunk, is rejected by the HEC endpoint. A `400` error is commonly caused by an index that has not been created in Splunk. One bad index can damage the batch, in this case, 1000 events, and prevent any of the data from being sent to Splunk. Make sure that the container logs are free of these kinds of errors in production. You can use the alternate HEC debug destination to help debug this condition by sending direct "curl" commands to the HEC endpoint outside of the SC4S setting.

## Issue: Invalid SC4S listening ports

[SC4S exclusively grants a port to a device when `SC4S_LISTEN_{vendor}_{product}_{TCP/UDP/TLS}_PORT={port}`](https://splunk.github.io/splunk-connect-for-syslog/main/sources/#unique-listening-ports).

During startup, SC4S validates that listening ports are configured correctly, and shows any issues in container logs.

You will receive an error message similar to the following if listening ports for `MERAKI SWITCHES` are configured incorrectly:
```
SC4S_LISTEN_MERAKI_SWITCHES_TCP_PORT: Wrong port number, don't use default port like (514,614,6514)
SC4S_LISTEN_MERAKI_SWITCHES_UDP_PORT: 7000 is not unique and has already been used for another source
SC4S_LISTEN_MERAKI_SWITCHES_TLS_PORT: 999999999999 must be integer within the range (0, 10000)
```

##  Issue: SC4S local disk resource issues
* Check the HEC connection to Splunk. If the connection is down for a long period of time, the local disk buffer used for backup will exhaust local
disk resources. The size of the local disk buffer is configured in the `env_file`: [Disk buffer configuration](https://splunk-connect-for-syslog.readthedocs.io/en/latest/configuration/#disk-buffer-variables)

* Check the `env_file` to see whether `SC4S_DEST_GLOBAL_ALTERNATES` is set to `d_hec_debug`,`d_archive`, or another file-based destination. Any of these settings will consume significant local disk space.

`d_hec_debug` and `d_archive` are organized by sourcetype; the `du -sh *` command can be used in each subdirectory to find the culprit. 

* Try rebuilding your SC4S volume:
```
podman volume rm splunk-sc4s-var
podman volume create splunk-sc4s-var
```
* Try pruning your containers:
```
podman system prune [--all]
``` 

## Issue: Incorrect SC4S/kernel UDP Input Buffer settings

UDP Input Buffer Settings let you request a certain buffer size when configuring the UDP sockets.  The kernel must have its parameters set to the same size or greater than what the syslog-ng configuration is requesting, or the following will occur in the SC4S logs:

```bash
/usr/bin/<podman|docker> logs SC4S
```
The following warning message is not a failure condition unless you are reaching the upper limit of your hardware performance.
```
The kernel refused to set the receive buffer (SO_RCVBUF) to the requested size, you probably need to adjust buffer related kernel parameters; so_rcvbuf='1703936', so_rcvbuf_set='425984'
```
Make changes to `/etc/sysctl.conf`, changing receive buffer values to 16 MB:

```
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360 
```
Run the following commands to implement your changes:
```
sysctl -p restart SC4S 
```

## Issue: Invalid SC4S TLS listener 

To verify the correct configuration of the TLS server use the following command. Replace the IP, FQDN, and port as appropriate:

```bash
<podman|docker> run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

## Issue: Unable to retrieve logs from non RFC-5424 compliant sources

If a data source you are trying to ingest claims it is RFC-5424 compliant but you get an "Error processing log message:" from SC4S, this message indicates that the data source still violates the RFC-5424 standard in some way. In this case, the underlying syslog-ng process will send an error event, with the location of the error in the original event highlighted with `>@<` to indicate where the error occurred. Here is an example error message:

```
{ [-]
   ISODATE: 2020-05-04T21:21:59.001+00:00
   MESSAGE: Error processing log message: <14>1 2020-05-04T21:21:58.117351+00:00 arcata-pks-cluster-1 pod.log/cf-workloads/logspinner-testing-6446b8ef - - [kubernetes@47450 cloudfoundry.org/process_type="web" cloudfoundry.org/rootfs-version="v75.0.0" cloudfoundry.org/version="eae53cc3-148d-4395-985c-8fef0606b9e3" controller-revision-hash="logspinner-testing-6446b8ef05-7db777754c" cloudfoundry.org/app_guid="f71634fe-34a4-4f89-adac-3e523f61a401" cloudfoundry.org/source_type="APP" security.istio.io/tlsMode="istio" statefulset.kubernetes.io/pod-n>@<ame="logspinner-testing-6446b8ef05-0" cloudfoundry.org/guid="f71634fe-34a4-4f89-adac-3e523f61a401" namespace_name="cf-workloads" object_name="logspinner-testing-6446b8ef05-0" container_name="opi" vm_id="vm-e34452a3-771e-4994-666e-bfbc7eb77489"] Duration 10.00299412s TotalSent 10 Rate 0.999701 
   PID: 33
   PRI: <43>
   PROGRAM: syslog-ng
}
``` 

In this example the error can be seen in the snippet `statefulset.kubernetes.io/pod-n>@<ame`. The error states that the "SD-NAME" (the left-hand side of the name=value pairs) cannot be longer than 32 printable ASCII characters, and the indicated name exceeds that. Ideally you should address this issue with the vendor, however, you can add an exception to the SC4S filter log path or an alternative workaround log path created for the data source.

In this example, the reason `RAWMSG` is not shown in the fields above is because this error message is coming from syslog-ng itself. In messages of the type `Error processing log message:` where the PROGRAM is shown as `syslog-ng`, your incoming message is not RFC-5424 compliant.


### Issue: Terminal is overwhelmed by metrics and internal processing messages in a custom environment configuration

In non-containerized SC4S deployments, if you try to start the SC4S service, the terminal may be overwhelmed by the internal and metrics logs. Example of the issue can be found here: [Github Terminal abuse issue](https://github.com/splunk/splunk-connect-for-syslog/issues/1954)

To resolve this, set following property in `env_file`:
```
SC4S_SEND_METRICS_TERMINAL=no
```

Restart SC4S. 

* NOTE:  This symptom will recur if `SC4S_DEBUG_CONTAINER` is set to "yes". Use the CLI `podman` or `docker` commands directly to start/stop SC4S.

### Issue: You are missing CEF logs that are not RFC compliant

1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_CEF=yes
```

2. Restart SC4S.


### Issue: You are missing VMWARE CB-PROTECT logs that are not RFC compliant

1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_VMWARE_CB_PROTECT=yes
```

2. Restart SC4S.

### Issue: You are missing CISCO IOS logs that are not RFC compliant

1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_CISCO=yes
```
2. Restart SC4S.

### Issue: You are missing VMWARE VSPHERE logs that are not RFC compliant

1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_VMWARE_VSPHERE=yes
```

2. Restart SC4S.

### Issue: You are missing RAW BSD logs that are not RFC compliant

1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_RAW_BSD=yes
```

2. Restart SC4S.

### Issue: You are missing RAW XML logs that are not RFC compliant
1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_XML=yes
```

2. Restart SC4S.

### Issue: You are missing HPE JETDIRECT logs that are not RFC compliant

1. To resolve this, set following property in `env_file`:
```
SC4S_DISABLE_DROP_INVALID_HPE=yes
```

2. Restart SC4S and it will not drop any invalid HPE JETDIRECT format.

NOTE: Please use only in this case of exception and this is splunk-unsupported feature. Also this setting might impact SC4S performance.

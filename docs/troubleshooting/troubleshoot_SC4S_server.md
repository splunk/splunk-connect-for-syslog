# SC4S Server Startup and Operational Validation

The following sections will guide the administrator to the most commons solutions to startup and
operational issues with SC4S.  In general, if you are just starting out with SC4S and wish to
simply run with the "stock" configuration, startup out of systemd is recommended.  If, on the other
hand, you are in the depths of a custom configuration of SC4S with significant modifications (such
as multiple unique ports for sources, hostname/CIDR block configuration for sources, new log paths,
etc.) then it is best to start SC4S with the container runtime command (`podman` or `docker`)
directly from the command line (below).  When you are satisfied with the operation, a transition to
systemd can then be made.

## systemd Errors During SC4S Startup 
Most issues that occur with startup and operation of sc4s typically involve syntax errors or duplicate listening ports.  If you are
running out of systemd, you may see this at startup:

```bash
[root@sc4s syslog-ng]# systemctl start sc4s
Job for sc4s.service failed because the control process exited with error code. See "systemctl status sc4s.service" and "journalctl -xe" for details.
```
Follow the checks below to resolve the issue:

### Is the SC4S container running?
There may be nothing untoward after starting with systemd, but the container is not running at all
after checking with `podman logs SC4S` or `podman ps`.  A more informative command than `journalctl -xe` is the following,
```
journalctl -b -u sc4s | tail -100
```
which will print the last 100 lines of the system journal in far more detail, which should be sufficient to see the specific failure
(syntax or runtime) and guide you in troubleshooting why the container exited unexpectedly.

### Does the SC4S container start (and run) properly outside of the systemd service environment? 
As an alternative to launching via systemd during the initial installation phase, you may wish to test the container startup outside of the
systemd startup environment. This alternative should be considered required when undergoing heavy troubleshooting or log path development (e.g.
when `SC4S_DEBUG_CONTAINER` is set to "yes").  The following command will launch the container directly from the CLI.
This command assumes the local mounted directories are set up as shown in the "getting started" examples; adjust for your local requirements:

```bash
/usr/bin/podman run \
    -v splunk-sc4s-var:/var/lib/syslog-ng \
    -v /opt/sc4s/local:/etc/syslog-ng/conf.d/local:z \
    -v /opt/sc4s/archive:/var/lib/syslog-ng/archive:z \
    -v /opt/sc4s/tls:/etc/syslog-ng/tls:z \
    --env-file=/opt/sc4s/env_file \
    --network host \
    --name SC4S \
    --rm splunk/scs:latest
```

If you are using docker, substitute "docker" for "podman" for the container runtime command above.

### Is the container still running (when systemd thinks it's not)?

In some instances, (particularly when `SC4S_DEBUG_CONTAINER=yes`) an SC4S container might not shut down completely when starting/stopping
out of systemd, and systemd will attempt to start a new container when one is already running with the `SC4S` name.
You will see this type of output when viewing the journal after a failed start caused by this condition, or a similar message when the container
is run directly from the CLI:

```
Jul 15 18:45:20 sra-sc4s-alln01-02 podman[11187]: Error: error creating container storage: the container name "SC4S" is already in use by "894357502b2a7142d097ea3ca1468d1cb4fbc69959a9817a1bbe145a09d37fb9". You have to remove that container...
Jul 15 18:45:20 sra-sc4s-alln01-02 systemd[1]: sc4s.service: Main process exited, code=exited, status=125/n/a
```

To rectify this, simply execute
```
podman rm -f SC4S
```

SC4S should then start normally.

* NOTE:  This symptom will recur if `SC4S_DEBUG_CONTAINER` is set to "yes".  _Do not_ attempt to use systemd when this variable is set; use the
CLI `podman` or `docker` commands directly to start/stop SC4S.

## HEC/token connection errors (AKA “No data in Splunk”)

SC4S performs basic HEC connectivity and index checks at startup.  These indicate general connection issues and indexes that may not be
accessible and/or configured on the Splunk side.  To check the container logs which contain the results of these tests, run:

```bash
/usr/bin/<podman|docker> logs SC4S
```

and note the output.  You will see entries similar to these:

```
SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful; checking indexes...

SC4S_ENV_CHECK_INDEX: Checking email {"text":"Incorrect index","code":7,"invalid-event-number":1}
SC4S_ENV_CHECK_INDEX: Checking epav {"text":"Incorrect index","code":7,"invalid-event-number":1}
SC4S_ENV_CHECK_INDEX: Checking main {"text":"Success","code":0}
```

Note the specifics of the indexes that are not configured correctly, and rectify in the Splunk configuration.  If this is not addressed
properly, you may see output similar to the below when data flows into sc4s:

```
Mar 16 19:00:06 b817af4e89da syslog-ng[1]: Server returned with a 4XX (client errors) status code, which means we are not authorized or the URL is not found.; url='https://splunk-instance.com:8088/services/collector/event', status_code='400', driver='d_hec#0', location='/opt/syslog-ng/etc/conf.d/destinations/splunk_hec.conf:2:5'
Mar 16 19:00:06 b817af4e89da syslog-ng[1]: Server disconnected while preparing messages for sending, trying again; driver='d_hec#0', location='/opt/syslog-ng/etc/conf.d/destinations/splunk_hec.conf:2:5', worker_index='4', time_reopen='10', batch_size='1000'
```
This is an indication that the standard `d_hec` destination in syslog-ng (which is the route to Splunk) is being rejected by the HEC endpoint.
A `400` error (not 404) is normally caused by an index that has not been created on the Splunk side.  This can present a serious problem, as
just _one_ bad index will "taint" the entire batch (in this case, 1000 events) and prevent _any_ of them from being sent to Splunk.  _It is
imperative that the container logs be free of these kinds of errors in production._ You can use the alternate HEC debug destination (below)
to help debug this condition by sending direct "curl" commands to the HEC endpoint outside of the SC4S setting.

## Invalid SC4S listen ports

[SC4S exclusively grant a port to a device when `SC4S_LISTEN_{vendor}_{product}_{TCP/UDP/TLS}_PORT={port}`](https://splunk.github.io/splunk-connect-for-syslog/main/sources/#unique-listening-ports).

During startup, SC4S validates that listening ports are configured correctly, and in case of misconfiguration, you will be able see any issues in container logs.

You will receive an error message similar to the following if listening ports for `MERAKI SWITCHES` are configured incorrectly:
```
SC4S_LISTEN_MERAKI_SWITCHES_TCP_PORT: Wrong port number, don't use default port like (514,614,6514)
SC4S_LISTEN_MERAKI_SWITCHES_UDP_PORT: 7000 is not unique and has already been used for another source
SC4S_LISTEN_MERAKI_SWITCHES_TLS_PORT: 999999999999 must be integer within the range (0, 10000)
```

##  SC4S Local Disk Resource Considerations
* Check the HEC connection to Splunk. If the connection is down for a long period of time, the local disk buffer used for backup will exhaust local
disk resources.  The size of the local disk buffer is configured in the env_file: [Disk buffer configuration](https://splunk-connect-for-syslog.readthedocs.io/en/latest/configuration/#disk-buffer-variables)

* Check the env_file to see if `SC4S_DEST_GLOBAL_ALTERNATES` is set to `d_hec_debug`,`d_archive` or other file-based destination; all of these will
consume significant local disk space.

`d_hec_debug` and `d_archive` are organized by sourcetype; the `du -sh *` command can be used in each subdirectory to find the culprit. 

* Try rebuilding sc4s volume
```
podman volume rm splunk-sc4s-var
podman volume create splunk-sc4s-var
```
* Try pruning containers
```
podman system prune [--all]
``` 

## SC4S/kernel UDP Input Buffer Settings

SC4S has a setting that requests a certain buffer size when configuring the UDP sockets.  The kernel must have its parameters set to at least the
same size (or greater) than the syslog-ng config is requesting, or the following will occur in the SC4S logs:

```bash
/usr/bin/<podman|docker> logs SC4S
```
Note the output. The following warning message is not a failure condition unless we are reaching the upper limit of hardware performance.
```
The kernel refused to set the receive buffer (SO_RCVBUF) to the requested size, you probably need to adjust buffer related kernel parameters; so_rcvbuf='1703936', so_rcvbuf_set='425984'
```
Make changes to /etc/sysctl.conf. Changing receive buffer values here to 16 MB:

```
net.core.rmem_default = 17039360
net.core.rmem_max = 17039360 
```
Run following commands for changes to be affected.
```
sysctl -p restart SC4S 
```

## SC4S TLS Listener Validation

To verify the correct configuration of the TLS server use the following command. Replace the IP, FQDN,
and port as appropriate:

```bash
<podman|docker> run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

## Timezone mismatch in events
By default, SC4S resolves the timezone to GMT. If customer have a preference to use local TZ then set the user TZ preference in Splunk during search time rather than at index time. 
[Timezone config documentation](https://docs.splunk.com/Documentation/Splunk/8.0.4/Data/ApplyTimezoneOffsetstotimestamps)

## Dealing with non RFC-5424 compliant sources

If a data source you are trying to ingest claims it is RFC-5424 compliant but you are getting an "Error processing log message:" from SC4S,
the message violates the standard in some way.  Unfortunately multiple vendors claim RFC-5424 compliance without fully testing that they are.
In this case, the underlying syslog-ng process will send an error event, with the location of the error in the original event highlighted with
`>@<` to indicate where the error occurred. Here is an example error message:

```
{ [-]
   ISODATE: 2020-05-04T21:21:59.001+00:00
   MESSAGE: Error processing log message: <14>1 2020-05-04T21:21:58.117351+00:00 arcata-pks-cluster-1 pod.log/cf-workloads/logspinner-testing-6446b8ef - - [kubernetes@47450 cloudfoundry.org/process_type="web" cloudfoundry.org/rootfs-version="v75.0.0" cloudfoundry.org/version="eae53cc3-148d-4395-985c-8fef0606b9e3" controller-revision-hash="logspinner-testing-6446b8ef05-7db777754c" cloudfoundry.org/app_guid="f71634fe-34a4-4f89-adac-3e523f61a401" cloudfoundry.org/source_type="APP" security.istio.io/tlsMode="istio" statefulset.kubernetes.io/pod-n>@<ame="logspinner-testing-6446b8ef05-0" cloudfoundry.org/guid="f71634fe-34a4-4f89-adac-3e523f61a401" namespace_name="cf-workloads" object_name="logspinner-testing-6446b8ef05-0" container_name="opi" vm_id="vm-e34452a3-771e-4994-666e-bfbc7eb77489"] Duration 10.00299412s TotalSent 10 Rate 0.999701 
   PID: 33
   PRI: <43>
   PROGRAM: syslog-ng
}
``` 

In this example the error can be seen in the snippet `statefulset.kubernetes.io/pod-n>@<ame`. Looking at the spec for RFC5424, it states that
the "SD-NAME" (the left-hand side of the name=value pairs) cannot be longer than 32 printable ASCII characters. In this message, the indicated
name exceeds that. Unfortunately, this is a spec violation on the part of the vendor. Ideally the vendor would address this violation so their
logs would be RFC-5424 compliant. Alternatively, an exception could be added to the SC4S filter log path (or an alternative (workaround) log
path created) for the data source if the vendor can’t/won’t fix the defect.

In this example, the reason `RAWMSG` is not shown in the fields above is because this error message is coming from syslog-ng itself --
_not_ the filter/log path. In messages of the type `Error processing log message:` where the PROGRAM is shown as `syslog-ng`, that is the
clue your incoming message is not RFC-5424 compliant (though it's often close, as is the case here).


### In BYOE the metrics/internal processing message are abusing the terminal , how to fix this?

In BYOE, when we try to start sc4s service , the terminal is getting abused from the internal and metrics log
Example of the issue is [Github Terminal abuse issue](https://github.com/splunk/splunk-connect-for-syslog/issues/1954)

To rectify this, Please set following property in env_file
```
SC4S_SEND_METRICS_TERMINAL=no
```

Restart SC4S and it will not send any more metrics data to Terminal.

* NOTE:  This symptom will recur if `SC4S_DEBUG_CONTAINER` is set to "yes".  _Do not_ attempt to use systemd when this variable is set; use the
CLI `podman` or `docker` commands directly to start/stop SC4S.

## SC4S dropping invalid events

### Sometimes you notice you are missing some CEF logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_CEF=yes
```

Restart SC4S and it will not drop any invalid CEF format.



### If you notice you are missing some VMWARE CB-PROTECT logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_VMWARE_CB_PROTECT=yes
```

Restart SC4S and it will not drop any invalid VMWARE CB-PROTECT format.

### If you notice you are missing some CISCO IOS logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_CISCO=yes
```

Restart SC4S and it will not drop any invalid CISCO IOS format.

### If you notice you are missing some VMWARE VSPHERE logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_VMWARE_VSPHERE=yes
```

Restart SC4S and it will not drop any invalid VMWARE VSPHERE format.

### If you notice you are missing some RAW BSD logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_RAW_BSD=yes
```

Restart SC4S and it will not drop any invalid RAW BSD format.

### If you notice you are missing some RAW XML logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_XML=yes
```

Restart SC4S and it will not drop any invalid RAW XML format.

### If you notice you are missing some HPE JETDIRECT logs which are not RFC compliant but logs are important, how to fix this?

To rectify this, Please set following property in env_file
```
SC4S_DISABLE_DROP_INVALID_HPE=yes
```

Restart SC4S and it will not drop any invalid HPE JETDIRECT format.

**NOTE: Please use only in this case of exception and this is splunk-unsupported feature. Also this setting might impact SC4S performance.**

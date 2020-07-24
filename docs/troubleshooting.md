#Troubleshooting 

## General

Prior to production deployment, it is easier to gauge proper operation outside of the systemd startup environment.  systemctl/systemd
make it difficult to see the error output of problematic services, so rather than "fight it" there, it's best to confirm proper
operation directly on the CLI.

To test the container outside of the systemd startup environment, you can run the following to test the syntax
of the container.  These commands assume the local mounted directories are set up as shown in the gettingstarted
examples:

```bash
/usr/bin/podman run -p 514:514 -p 514:514/udp -p 6514:6514 -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp \
    --env-file=/opt/sc4s/env_file \
    -v splunk-sc4s-var:/opt/syslog-ng/var \
    -v /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z \
    -v /opt/sc4s/archive:/opt/syslog-ng/var/archive:z \
    --name SC4S_preflight \
    --rm splunk/scs:latest -s
```

and you can run

```bash
/usr/bin/podman run -p 514:514 -p 514:514/udp -p 6514:6514 -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp \
    --env-file=/opt/sc4s/env_file \
    -v splunk-sc4s-var:/opt/syslog-ng/var \
    -v /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z \
    -v /opt/sc4s/archive:/opt/syslog-ng/var/archive:z \
    --name SC4S \
    --rm splunk/scs:latest
```

to test the final image.  If you are using podman, substitute "podman" for "docker" for the container runtime command above.

### Verification of TLS Server

To verify the correct configuration of the TLS server use the following command. Use `podman` or `docker` and replace the IP, FQDN,
and port as appropriate:

```bash
<podman|docker> run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

## Validating HEC/token issues (AKA "No data in Splunk")

The first thing to check are the container logs themselves, where stdout from the underlying syslog-ng is written by default.  To do this,
run:

```bash
/usr/bin/podman logs SC4S
```

and note the output.  You may see entries similar to these:
```
Mar 16 19:00:06 b817af4e89da syslog-ng[1]: Server returned with a 4XX (client errors) status code, which means we are not authorized or the URL is not found.; url='https://splunk-instance.com:8088/services/collector/event', status_code='400', driver='d_hec#0', location='/opt/syslog-ng/etc/conf.d/destinations/splunk_hec.conf:2:5'
Mar 16 19:00:06 b817af4e89da syslog-ng[1]: Server disconnected while preparing messages for sending, trying again; driver='d_hec#0', location='/opt/syslog-ng/etc/conf.d/destinations/splunk_hec.conf:2:5', worker_index='4', time_reopen='10', batch_size='1000'
```
This is an indication that the standard `d_hec` destination in syslog-ng (which is the route to Splunk) is being rejected by the HEC endpoint.
A `400` error (not 404) is normally caused by an index that has not been created on the Splunk side, and is a common occurrence in new
installations.  This can present a serious problem, as just _one_ bad index will "taint" the entire batch (in this case, 1000 events) and
prevent _any_ of them from being sent to Splunk.  _It is imperative that the container logs be free of these kinds of errors in production._

### Enabling the Alternate Debug Destination

To help debug why the `400` errors are ocurring, it is helpful to enable an alternate destination for syslog traffic that will write
the contents of the full JSON payload that is intended to be sent to Splunk via HEC.  This destination will contain each event, repackaged
as a `curl` command that can be run directly on the command line to see what the response from the HEC endpoint is.  To do this, set
`SC4S_DEST_GLOBAL_ALTERNATES=d_hec_debug` in the `env_file` and restart sc4s.  When set, all data destined for Splunk will also be written to
`/opt/sc4s/archive/debug`, and will be further categorized in subdirectories by sourcetype.  Here are the things to check:

* In `/opt/sc4s/archive/debug`, you will see directories for each sourcetype that sc4s has collected. If you recognize any that you
don't expect, check to see that the index is created in Splunk, or that a `lastChanceIndex` is created and enabled.  This is the
cause for almost _all_ `400` errors.
* If you continue to the individual log entries in these directories, you will see entries of the form
```bash
curl -k -u "sc4s HEC debug:a778f63a-5dff-4e3c-a72c-a03183659e94" "https://splunk.smg.aws:8088/services/collector/event" -d '{"time":"1584556114.271","sourcetype":"sc4s:events","source":"SC4S:s_internal","index":"main","host":"e3563b0ea5d8","fields":{"sc4s_syslog_severity":"notice","sc4s_syslog_facility":"syslog","sc4s_loghost":"e3563b0ea5d8","sc4s_fromhostip":"127.0.0.1"},"event":"syslog-ng starting up; version='3.28.1'"}'
```
* These commands, with minimal modifications (e.g. multiple URLs specified or elements that needs shell escapes) can be run directly on the
command line to determine what, exactly, the HEC endpoint is returning.  This can be used to refine th index or other parameter to correct the
problem.

## "Exec" into the container

You can confirm how the templating process created the actual syslog-ng config files that are in use by "exec'ing in" to the container
and navigating the syslog-ng config filesystem directly.  To do this, run
```bash
/usr/bin/podman exec -it SC4S /bin/bash
```
and navigate to `/opt/syslog-ng/etc/` to see the actual config files in use.  If you are adept with container operations and syslog-ng
itself, you can modify files directly and reload syslog-ng with the command `kill -1 1` in the container.
You can also run the `/entrypoint.sh` script by hand (or a subset of it, such as everything
but syslog-ng) and have complete control over the templating and underlying syslog-ng process.
This is an advanced topic and futher help can be obtained via the github issue tracker and Slack channels.

When debugging a configuration syntax issue at startup the container must remain running. This can be enabled by adding `SC4S_DEBUG_CONTAINER=yes` to the `env_file`.

## Dealing with non RFC-5424 compliant sources

If a data source you are trying to ingest via SC4S claims it is RFC-5424 compliant however you are getting a log message processing error this might be happening.

Unfortunately multiple vendors claim RFC-5424 compliance without fully testing that they are. The SC4S error message uses >@< to indicate where the error occurred. Here is an example error message…

{ [-]
   ISODATE: 2020-05-04T21:21:59.001+00:00
   MESSAGE: Error processing log message: <14>1 2020-05-04T21:21:58.117351+00:00 arcata-pks-cluster-1 pod.log/cf-workloads/logspinner-testing-6446b8ef - - [kubernetes@47450 cloudfoundry.org/process_type="web" cloudfoundry.org/rootfs-version="v75.0.0" cloudfoundry.org/version="eae53cc3-148d-4395-985c-8fef0606b9e3" controller-revision-hash="logspinner-testing-6446b8ef05-7db777754c" cloudfoundry.org/app_guid="f71634fe-34a4-4f89-adac-3e523f61a401" cloudfoundry.org/source_type="APP" security.istio.io/tlsMode="istio" statefulset.kubernetes.io/pod-n>@<ame="logspinner-testing-6446b8ef05-0" cloudfoundry.org/guid="f71634fe-34a4-4f89-adac-3e523f61a401" namespace_name="cf-workloads" object_name="logspinner-testing-6446b8ef05-0" container_name="opi" vm_id="vm-e34452a3-771e-4994-666e-bfbc7eb77489"] Duration 10.00299412s TotalSent 10 Rate 0.999701 
   PID: 33
   PRI: <43>
   PROGRAM: syslog-ng
} 

In this example the error can be found in, statefulset.kubernetes.io/pod-n>@<ame. Looking at the spec for RFC5424, it states that the "SD-NAME" (the left-hand side of the name=value pairs) cannot be longer than 32 printable ASCII characters. In this message, the indicated name exceeds that. Unfortunately, this is a spec violation on the part of the vendor. Ideally the vendor would fix this as a defect so their logs would be RFC-5424 compliant. Alternatively, an exception could be added to the SC4S filter log path for the data source if the vendor can’t/won’t fix the defect. 

In this example, the reason SC4S_SOURCE_STORE_RAWMSG did not return anything is because this error message is coming from syslog-ng itself -- not the filter/log path. When you get messages of the type Error processing log message with the PROGRAM being syslog-ng that is the clue your incoming message is not RFC-5424 compliant (though it's often close, as is the case here).

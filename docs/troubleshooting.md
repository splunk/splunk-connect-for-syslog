#Troubleshooting 

## Not getting starting up message in Splunk!

### Are there any syntax errors or duplicate listening ports?
Most issues that occur with startup and operation of sc4s typically involve syntax errors or duplicate listening ports.  If you are
running out of systemd, you may see this at startup:
```bash
[root@sc4s syslog-ng]# systemctl start sc4s
Job for sc4s.service failed because the control process exited with error code. See "systemctl status sc4s.service" and "journalctl -xe" for details.
```
### Is your container running?
There may be nothing untoward after starting with systemd, but the container is not running at all
after checking with `podman logs SC4S` or `podman ps`.  A more informative command than `journalctl -xe` is the following,
```
journalctl -b -u sc4s | tail -100
```
which will print the last 100 lines of the system journal in far more detail, which should be sufficient to see the specific failure
(syntax or runtime) and guide you in troubleshooting why the container exited unexpectedly.

### Is your container working outside of the systemd startup environment? 
As an alternative to launching via systemd during the initial installation phase, you may wish to test the container startup outside of the
systemd startup environment. The following command will launch the container directly from the CLI.  This command assumes the local mounted
directories are set up as shown in the "getting started" examples:

```bash
/usr/bin/podman run -p 514:514 -p 514:514/udp -p 6514:6514 -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp \
    --env-file=/opt/sc4s/env_file \
    -v splunk-sc4s-var:/opt/syslog-ng/var \
    -v /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z \
    -v /opt/sc4s/archive:/opt/syslog-ng/var/archive:z \
    --name SC4S \
    --rm splunk/scs:latest
```

If you are using docker, substitute "docker" for "podman" for the container runtime command above.

### Are there any stale containers in your environment? (podman)

In rare instances, (especially when starting/stopping often) an SC4S container might not shut down completely when using podman, leaving a
"stale" container behind that is denoted by a very long ID string.  You will see this type of output when viewing the journal after a failed
start caused by this condition, or a similar message when the container is run directly from the CLI:

```
Jul 15 18:45:20 sra-sc4s-alln01-02 podman[11187]: Error: error creating container storage: the container name "SC4S" is already in use by "894357502b2a7142d097ea3ca1468d1cb4fbc69959a9817a1bbe145a09d37fb9". You have to remove that container...
Jul 15 18:45:20 sra-sc4s-alln01-02 systemd[1]: sc4s.service: Main process exited, code=exited, status=125/n/a
```

To rectify this, simply execute
```
podman rm -f 894357502b2a7142d097ea3ca1468d1cb4fbc69959a9817a1bbe145a09d37fb9
```

replacing the long string with whatever container ID is shown in your error message.  SC4S should then start normally.

### Are there any HEC errors in the podman logs?

SC4S performs basic HEC connectivity and index checks at startup.  These indicate general connection issues and indexes that may not be
accesible and/or configured on the Splunk side.  To check the container logs which contain the results of these tests, run:

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
imperative that the container logs be free of these kinds of errors in production._

### Is SC4S server out of space?
Check the connection to Splunk. If the connection is lost for a long period it will lead to increase in disk space due to disk buffer backup. 
Adjust the size of the disk buffer using env_file. [Disk buffer configuration](https://splunk-connect-for-syslog.readthedocs.io/en/master/configuration/#disk-buffer-variables)

Check env_file if `SC4S_DEST_GLOBAL_ALTERNATES=d_hec_debug` is enabled and hence archive is consuming disk space.

Check the method consuming disk space use `df -h` and then `du -sh *` to find out what's causing it.

Try rebuilding sc4s volume.
```
podman volume rm splunk-sc4s-var
podman volume create splunk-sc4s-var
```
Try pruning containers
```
podman system prune
``` 

### Are there any kernel memory warnings?

```bash
/usr/bin/<podman|docker> logs SC4S
```
Note the output. The following warning message is not a failure condition unless we are reaching the upper limit of hardware performance.
```
The kernel refused to set the receive buffer (SO_RCVBUF) to the requested size, you probably need to adjust buffer related kernel parameters; so_rcvbuf='1703936', so_rcvbuf_set='425984'
```
Make changes to /etc/sysctl.conf. Changing receive buffer values here to 16 MB:

```
net.core.rmem_default = 1703936
net.core.rmem_max = 1703936. 
```
Run following commands for changes to be affected.
```
sysctl -p restart SC4S 
```

## Are there events with incorrect timezone?
By default, SC4S resolves the timezone to GMT. If customer have a preference to use local TZ then set the user TZ preference in Splunk during search time rather than at index time. 
[Timezone config documentation](https://docs.splunk.com/Documentation/Splunk/8.0.4/Data/ApplyTimezoneOffsetstotimestamps)

## Is your TLS server configured correctly?

To verify the correct configuration of the TLS server use the following command. Use `podman` or `docker` and replace the IP, FQDN,
and port as appropriate:

```bash
<podman|docker> run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

## Enabling the Alternate Debug Destination

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

## Obtaining "On-the-wire" Raw Events

In almost all cases during development or troubleshooting, you will need to obtain samples of the messages exactly as they are received by
SC4S. These "raw" events contain the full syslog message (including the `<PRI>` preamble) and differs from those that appear in Splunk after
processing by sc4s and/or Splunk. This is the only way to determine if SC4S parsers and filters are operating correctly, as raw messages are
needed for "playback" when testing. In addition, the community supporting SC4S will always first ask for raw samples (kind of like the way
Splunk support always asks for "diags") before any development or troubleshooting exercise.

Here are some options for obtaining raw logs for one or more sourcetypes:

* Run `tcpdump` on the collection interface and display the results in ASCII.  You will see events of the form
```
<165>1 2007-02-15T09:17:15.719Z router1 mgd 3046 UI_DBASE_LOGOUT_EVENT [junos@2636.1.1.1.2.18 username="user"] User 'user' exiting configuration mode
```
buried in the packet contents.

* Set the variable `SC4S_SOURCE_STORE_RAWMSG=yes` in `env_file` and restart sc4s.  This will store the raw message in a syslog-ng macro called
`RAWMSG` and will be displayed in Splunk for all `fallback` messages.  For most other sourcetypes, the `RAWMSG` is _not_ displayed, but can be
surfaced by changing the output template to one of the JSON variants (t_JSON_3164 or t_JSON_5424 depending on RFC message type). See
[SC4S metadata configuration](https://splunk-connect-for-syslog.readthedocs.io/en/develop/configuration/#sc4s-metadata-configuration) for
more details.

** IMPORTANT!  Be sure to turn off the `RAWMSG` variable when you are finished, as it doubles the memory and disk requirements of sc4s.  Do not
use in production!

* Lastly, you can enable the alternate destination `d_rawmsg` for one or more sourcetypes.  This destination will write the raw messages to the
container directory `/opt/syslog-ng/var/archive/rawmsg/<sourcetype>` (which is typically mapped locally to `/opt/sc4s/archive`).
Within this directory, the logs are organized by host and time.  This method can be useful when raw samples are needed for events that
partially parse (or parse into the wrong sourcetype) and the output template is not JSON (see above).

## "exec" into the container (advanced)

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
not the filter/log path. In messages of the type `Error processing log message:` where the PROGRAM is shown as `syslog-ng`, that is the
clue your incoming message is not RFC-5424 compliant (though it's often close, as is the case here).
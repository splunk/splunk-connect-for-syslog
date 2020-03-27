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
`/opt/sc4s/archived/debug`, and will be further categorized in subdirectories by sourcetype.  Here are the things to check:

* In `/opt/sc4s/archived/debug`, you will see directories for each sourcetype that sc4s has collected. If you recognize any that you
don't expect, check to see that the index is created in Splunk, or that a `lastChanceIndex` is created and enabled.  This is the
cause for almost _all_ `400` errors.
* If you continue to the individual log entries in these directories, you will see entries of the form
```bash
curl -k -u "sc4s HEC debug:a778f63a-5dff-4e3c-a72c-a03183659e94" "https://splunk.smg.aws:8088/services/collector/event" -d '{"time":"1584556114.271","sourcetype":"sc4s:events","source":"SC4S:s_internal","index":"main","host":"e3563b0ea5d8","fields":{"sc4s_syslog_severity":"notice","sc4s_syslog_facility":"syslog","sc4s_log_host":"e3563b0ea5d8","sc4s_fromhostip":"127.0.0.1"},"event":"syslog-ng starting up; version='3.26.1'"}'
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
itself, you can also modify files directly and reload syslog-ng with the command `kill -1 1` in the container.  This is an advanced topic
and futher help can be obtained via the github issue tracker and Slack channels.

## Run the container with a null entrypoint (Advanced!)

You can run the container without the usual entrypoint shell script by executing this command (modified to suit your environment):

```bash
/usr/bin/podman run -p 514:514 -p 514:514/udp -p 5000-5020:5000-5020 -p 5000-5020:5000-5020/udp --entrypoint=tail --env-file=/opt/sc4s/env_file -v /opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z --name SC4S --rm splunk/scs:latest -f /dev/null
```
From there, you can "exec" into the container (above) and run the `/entrypoint.sh` script by hand (or a subset of it, such as everything
but syslog-ng) and have complete control over the templating and underlying syslog-ng process.  Again, this is an advanced topic but can be
very useful for low-level troubleshooting.


#Configure Logging and Debug Resources
## Enabling the Alternate Debug Destination

To help debug why the `400` errors are ocurring, it is helpful to enable an alternate destination for syslog traffic that will write
the contents of the full JSON payload that is intended to be sent to Splunk via HEC.  This destination will contain each event, repackaged
as a `curl` command that can be run directly on the command line to see what the response from the HEC endpoint is.  

To do this, set `SC4S_DEST_GLOBAL_ALTERNATES=d_hec_debug` in the `env_file` and restart sc4s.  When set, all data destined for Splunk will also be written to
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

##Debug Commands
###Container Commands

- Container logs `sudo <docker/podman> logs SC4S`
- Exec into SC4S container `docker exec -it SC4S bash`
- Rebuilding SC4S volume.
```
<docker/podman> volume rm splunk-sc4s-var
<docker/podman> volume create splunk-sc4s-var
```
- Pull an image or a repository from a registry `docker pull splunk:scs:latest`
- Remove unused data `docker system prune`
- Load an image from a tar archive or STDIN `docker load <tar>`

### Linux services commands

- Check service status `systemctl status sc4s`
- Start service `systemctl start service`
- Stop service `systemctl stop service`
- Restart service `systemctl restart service`
- Enabling service at boot `systemctl enable sc4s`

###Query the systemd journal
journalctl -b -u sc4s

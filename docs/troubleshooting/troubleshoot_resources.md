# SC4S Logging and Troubleshooting Resources

## Helpful Linux and Container Commands

### Linux service (systemd) commands

- Check service status `systemctl status sc4s`
- Start service `systemctl start service`
- Stop service `systemctl stop service`
- Restart service `systemctl restart service`
- Enabling service at boot `systemctl enable sc4s`
- Query the system journal `journalctl -b -u sc4s`

### Container Commands

* NOTE:  All container commands below can be run with either runtime (`podman` or `docker`).

- Container logs `sudo podman logs SC4S`
- Exec into SC4S container `podman exec -it SC4S bash`
- Rebuilding SC4S volume
```
podman volume rm splunk-sc4s-var
podman volume create splunk-sc4s-var
```
- Pull an image or a repository from a registry `podman pull splunk:scs:latest`
- Remove unused data `podman system prune`
- Load an image from a tar archive or STDIN `podman load <tar>`

### Test Commands

Checking SC4S port using “nc”. Run this command where SC4S is hosted and check for data in Splunk for success and failure
```
echo '<raw_sample>' |nc <host> <port>
```

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
`RAWMSG` and will be displayed in Splunk for all `fallback` messages.
* For most other sourcetypes, the `RAWMSG` is _not_ displayed, but can be
surfaced by changing the output template to one of the JSON variants (t_JSON_3164 or t_JSON_5424 depending on RFC message type). See
[SC4S metadata configuration](https://splunk-connect-for-syslog.readthedocs.io/en/develop/configuration/#sc4s-metadata-configuration) for
more details.
* In order to send `RAWMSG` to Splunk regardless the sourcetype you can also temporarily place the following final filter in the local parsers' directory:
```conf
block parser app-finalfilter-fetch-rawmsg() {
    channel {
        rewrite {
            r_set_splunk_dest_default(
                template('t_fallback_kv')
            );
        };
    };
};

application app-finalfilter-fetch-rawmsg[sc4s-finalfilter] {
    parser { app-finalfilter-fetch-rawmsg(); };
};
```
With both `SC4S_SOURCE_STORE_RAWMSG=yes` in `/opt/sc4s/env_file` and this finalfilter placed in `/opt/sc4s/local/config/app_parsers` your restarted SC4S instance will add raw messages to all the messages sent to Splunk.

** IMPORTANT!  Be sure to turn off the `RAWMSG` variable when you are finished, as it doubles the memory and disk requirements of sc4s.  Do not
use `RAWMSG` in production!

* Lastly, you can enable the alternate destination `d_rawmsg` for one or more sourcetypes.  This destination will write the raw messages to the
container directory `/var/syslog-ng/archive/rawmsg/<sourcetype>` (which is typically mapped locally to `/opt/sc4s/archive`).
Within this directory, the logs are organized by host and time.

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
This is an advanced topic and further help can be obtained via the github issue tracker and Slack channels.

## Keeping a failed container running (even more advanced)

When debugging a configuration syntax issue at startup, it is often helpful to keep the container running after a syslog-ng startup failure.
In order to facilitate troubleshooting and make "on the fly" syslog-ng configuration changes from within a running container, the container
can be forced to remain running when syslog-ng fails to start (which normally terminates the container). This can be enabled by adding
`SC4S_DEBUG_CONTAINER=yes` to the `env_file`.  Use this capability in conjunction with "exec-ing" into the container described above.

* NOTE:  Do _not_ attempt to enable the debug container mode while running out of systemd.  Run the container manually from the CLI, as
`podman` or `docker` commands will be required to start, stop, and optionally clean up cruft left behind by the debug process.
Only when `SC4S_DEBUG_CONTAINER` is set to "no" (or completely unset) should systemd startup processing resume.

## Fix timezone 
Mismatch in TZ can occur if SC4S and logHost are not in same TZ. This is commonly occurring problem. To fix it one must 
create a filter using `sc4s-lp-dest-format-d_hec_fmt`. Example:

```
#filename: /opt/sc4s/local/config/app_parsers/rewriters/app-dest-rewrite-fix_tz_something.conf

block parser app-dest-rewrite-checkpoint_drop-d_fmt_hec_default() {    
    channel {
            rewrite { fix-time-zone("EST5EDT"); };
    };
};
application app-dest-rewrite-fix_tz_something-d_fmt_hec_default[sc4s-lp-dest-format-d_hec_fmt] {
    filter {
        match('checkpoint' value('fields.sc4s_vendor') type(string))                 <- this has to be customized
        and match('syslog' value('fields.sc4s_product') type(string))                <- this has to be customized
        and match('Drop' value('.SDATA.sc4s@2620.action') type(string))              <- this has to be customized
        and match('12.' value('.SDATA.sc4s@2620.src') type(string) flags(prefix) );  <- this has to be customized

    };    
    parser { app-dest-rewrite-fix_tz_something-d_fmt_hec_default(); };   
};
```


Or create a post-filter if destport, container, proto are not available in indexed fields: 

```
#filename: /opt/sc4s/local/config/app_parsers/rewriters/app-dest-rewrite-fix_tz_something.conf

block parser app-dest-rewrite-fortinet_fortios-d_fmt_hec_default() {
    channel {
            rewrite {
                  fix-time-zone("EST5EDT");
            };
    };
};

application app-dest-rewrite-device-d_fmt_hec_default[sc4s-postfilter] {
    filter {
         match("xxxx", value("fields.sc4s_destport") type(glob));  <- this has to be customized
    };
    parser { app-dest-rewrite-fortinet_fortios-d_fmt_hec_default(); };
};
```
Note that filter match statement should be aligned to your data!
Parser accepts timezone in formats: "America/New York" or "EST5EDT" (though not short form like "EST" only).

## Cyberark logs known issue
When the data is received on the indexers all the events are merged together into one. Please check the below link for configuration on cyberark side
https://cyberark-customers.force.com/s/article/00004289

## SC4S events dropping issue when another interface used to receive logs
When second / another interface used to receive syslog traffic, RPF (Reverse Path Forwarding filtering) in RHEL (configured as default configuration) was dropping the events.

Need to add static route for source device to point back dedicated syslog interface.
Reference: https://access.redhat.com/solutions/53031

## SC4S events not ingested in splunk from other VM
When data is transmitted through an echo message from the same instance, it is successfully sending data to splunk. However, when the echo is sent from a different instance, the data does not appear in splunk and no errors are reported in the logs.
To resolve this issue, it is essential to check whether an internal firewall is enabled. If an  internal firewall is active, it's important to verify whether the default port 514 or the port which you have used is blocked or not.
Here are some commands to check and enable, if not enabled:
```
#To list all the firewall ports
sudo firewall-cmd --list-all
#to enable 514 if its not enabled
sudo firewall-cmd --zone=public --permanent --add-port=514/udp
sudo firewall-cmd  --reload
```

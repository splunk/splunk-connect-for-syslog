#SC4S server issues
##Errors during SC4S Startup 
Most issues that occur with startup and operation of sc4s typically involve syntax errors or duplicate listening ports.  If you are
running out of systemd, you may see this at startup:

```bash
[root@sc4s syslog-ng]# systemctl start sc4s
Job for sc4s.service failed because the control process exited with error code. See "systemctl status sc4s.service" and "journalctl -xe" for details.
```
### Check if your container is running?
There may be nothing untoward after starting with systemd, but the container is not running at all
after checking with `podman logs SC4S` or `podman ps`.  A more informative command than `journalctl -xe` is the following,
```
journalctl -b -u sc4s | tail -100
```
which will print the last 100 lines of the system journal in far more detail, which should be sufficient to see the specific failure
(syntax or runtime) and guide you in troubleshooting why the container exited unexpectedly.

### Check if your container working outside of the systemd startup environment? 
As an alternative to launching via systemd during the initial installation phase, you may wish to test the container startup outside of the
systemd startup environment. The following commmand will launch the container directly from the CLI.  This command assumes the local mounted
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

### Check for Stale Containers (podman)

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

##  SC4S server out of space 
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

## Kernel memory warning

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

## Verification of TLS Server

To verify the correct configuration of the TLS server use the following command. Use `podman` or `docker` and replace the IP, FQDN,
and port as appropriate:

```bash
<podman|docker> run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

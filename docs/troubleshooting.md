#Troubleshooting 

## General

To test the container outside of the systemd startup environment, you can run the following to test the syntax
of the container.  These commands assume the local mounted directory is set up as shown in the gettingstarted
examples (and omits the disk buffer mount):

```
/usr/bin/docker run --env-file=/opt/sc4s/env_file -v "/opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z" --name SC4S_preflight --rm splunk/scs:latest -s
```

and you can run

```
/usr/bin/docker run --env-file=/opt/sc4s/env_file -v "/opt/sc4s/local:/opt/syslog-ng/etc/conf.d/local:z" --name SC4S --rm splunk/scs:latest
```

to test the final image.  These commands can help with container errors that are hidden in the systemd process.

### Verification of TLS Server

To verify the correct configuration of the TLS server use the following command. Replace the IP, FQDN, and port as appropriate

* Docker
```
docker run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

* Podman
```
podman run -ti drwetter/testssl.sh --severity MEDIUM --ip 127.0.0.1 selfsigned.example.com:6510
```

## Syslog-ng Metrics 

## Syslog-NG Events

## Container Events

# Monitoring

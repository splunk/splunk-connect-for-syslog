#Troubleshooting 

## General


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

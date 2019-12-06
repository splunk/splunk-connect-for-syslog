# Vendor - Juniper

## Product - Juniper JunOS

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | https://splunkbase.splunk.com/app/2847/                                 |
| JunOS TechLibrary | https://www.juniper.net/documentation/en_US/junos/topics/example/syslog-messages-configuring-qfx-series.html |

### Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| juniper:junos:firewall   | None                                                             |
| juniper:junos:idp        | None                                                             |

### Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| juniper_junos_flow         | juniper:junos:firewall | netfw          | none          |
| juniper_junos_idp          | juniper:junos:idp      | netids         | none          |
| juniper_junos_utm          | juniper:junos:firewall | netfw          | none          |

### Filter type

* MSG Parse: This filter parses message content


### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index as required.
* Follow vendor configuration steps per referenced Product Manual

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_JUNIPER_JUNOS_LEGACY_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined using legacy 3164 format|
| SC4S_LISTEN_JUNIPER_JUNOS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined using 5424 format |
| SC4S_ARCHIVE_JUNIPER_JUNOS | no | Enable archive to text for this specific source |
| SC4S_DEST_JUNIPER_JUNOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present; for Juniper JunOS ensure each host filter condition is verified

```
index=<asconfigured> sourcetype=juniper:junos:firewall | stats count by host
index=<asconfigured> sourcetype=juniper:junos:idp | stats count by host
```

Verify timestamp, and host values match as expected

## Product - Juniper NSM

| Ref            | Link                                                                    |
|----------------|-------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2847/                                 |
| NSM syslog KB  | http://kb.juniper.net/InfoCenter/index?page=content&id=KB11810          |

### Sourcetypes

| sourcetype       | notes                                                                 |
|------------------|-----------------------------------------------------------------------|
| juniper:nsm      | None                                                                  |
| juniper:nsm:idp  | None                                                                  |

### Sourcetype and Index Configuration

| key                    | sourcetype          | index          | notes         |
|------------------------|---------------------|----------------|---------------|
| juniper_nsm            | juniper:nsm         | netfw          | none          |
| juniper_nsm_idp        | juniper:nsm:idp     | netids         | none          |

### Filter type

* Juniper NSM products must be identified by host or ip assignment. Update the filter `f_juniper_nsm` or `f_juniper_nsm_idp` as required


### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index as required.
* Follow vendor configuration steps per Product Manual

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_JUNIPER_NSM_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_JUNIPER_NSM_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_JUNIPER_NSM | no | Enable archive to text for this specific source |
| SC4S_DEST_JUNIPER_NSM_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present; for Juniper NSM ensure each host filter condition is verified

```
index=<asconfigured> sourcetype=juniper:nsm | stats count by host
index=<asconfigured> sourcetype=juniper:nsm:idp | stats count by host
```

Verify timestamp, and host values match as expected

## Product - Juniper Netscreen

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2847/                                                                 |
| Netscreen Manual   | http://kb.juniper.net/InfoCenter/index?page=content&id=KB4759                                       |

### Sourcetypes

| sourcetype              | notes                                                                                          |
|-------------------------|------------------------------------------------------------------------------------------------|
| netscreen:firewall      | None                                                                                           |
| juniper:idp             | None                                                                                           |

### Sourcetype and Index Configuration

| key                    | sourcetype          | index          | notes         |
|------------------------|---------------------|----------------|---------------|
| juniper_netscreen      | netscreen:firewall  | netfw          | none          |
| juniper_idp            | juniper:idp         | netfw          | none          |

### Filter type

* Juniper Netscreen products must be identified by host or ip assignment. Update the filter `f_juniper_netscreen` or `f_juniper_idp` as required


### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index as required.
* Follow vendor configuration steps per Product Manual

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_JUNIPER_NETSCREEN_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_JUNIPER_NETSCREEN | no | Enable archive to text for this specific source |
| SC4S_DEST_JUNIPER_NETSCREEN_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present; for Juniper Netscreen products ensure each host filter condition is verified

```
index=<asconfigured> sourcetype=netscreen:firewall | stats count by host
index=<asconfigured> sourcetype=juniper:idp | stats count by host
```

Verify timestamp, and host values match as expected

## Product - Juniper SSLVPN

| Ref              | Link                                                                    |
|------------------|-------------------------------------------------------------------------|
| Splunk Add-on    | https://splunkbase.splunk.com/app/2847/                                 |
| Pulse Secure KB  | https://kb.pulsesecure.net/articles/Pulse_Secure_Article/KB22227        |

### Sourcetypes

| sourcetype       | notes                                                                 |
|------------------|-----------------------------------------------------------------------|
| juniper:sslvpn   | None                                                                  |

### Sourcetype and Index Configuration

| key                    | sourcetype          | index          | notes         |
|------------------------|---------------------|----------------|---------------|
| juniper_sslvpn         | juniper:sslvpn      | netfw          | none          |

### Filter type

* MSG Parse: This filter parses message content


### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index as required.
* Follow vendor configuration steps per referenced Product Manual

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_JUNIPER_JUNOS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_JUNIPER_JUNOS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_JUNIPER_JUNOS | no | Enable archive to text for this specific source |
| SC4S_DEST_JUNIPER_JUNOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present; for Juniper SSL VPN ensure each host filter condition is verified

```
index=<asconfigured> sourcetype=juniper:sslvpn | stats count by host
```

Verify timestamp, and host values match as expected
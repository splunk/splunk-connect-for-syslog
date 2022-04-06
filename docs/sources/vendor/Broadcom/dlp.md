# Symantec DLP

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on Symatec DLP | https://splunkbase.splunk.com/app/3029/                                                      |
| Source doc | https://knowledge.broadcom.com/external/article/159509/generating-syslog-messages-from-data-los.html                                    |


## Sourcetypes

| sourcetype           | notes                                                                                                   |
|----------------------|---------------------------------------------------------------------------------------------------------|
| symantec:dlp:syslog  | None                                                                                                    |

## Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| symantec_dlp   | symantec:dlp:syslog      | netauth          | none          |

## Option 1: Correct Source syslog formats

### Syslog Alert Response

Login to Symantec DLP and edit the Syslog Response rule. The default configuration will appear as follows

```text
$POLICY$^^$INCIDENT_ID$^^$SUBJECT$^^$SEVERITY$^^$MATCH_COUNT$^^$RULES$^^$SENDER$^^$RECIPIENTS$^^$BLOCKED$^^$FILE_NAME$^^$PARENT_PATH$^^$SCAN$^^$TARGET$^^$PROTOCOL$^^$INCIDENT_SNAPSHOT$
```

DO NOT replace the text prepend the following literal

```text
SymantecDLPAlert: 
```

Result note the space between ':' and '$'

```text
SymantecDLPAlert: $POLICY$^^$INCIDENT_ID$^^$SUBJECT$^^$SEVERITY$^^$MATCH_COUNT$^^$RULES$^^$SENDER$^^$RECIPIENTS$^^$BLOCKED$^^$FILE_NAME$^^$PARENT_PATH$^^$SCAN$^^$TARGET$^^$PROTOCOL$^^$INCIDENT_SNAPSHOT$
```

### Syslog System events

* Navigate to the installed directory, for example `<drive>:\SymantecDLP\Protect\config` directory on Windows or the `/opt/SymantecDLP/Protect/config` directory on Linux.
* Open the `Manager.properties` file.
* Comment out any uncommented line starting with `systemevent.syslog.format`
* Add the following line `systemevent.syslog.format= {0.EN_US} SymantecDLP: {1.EN_US} - {2.EN_US}`
* Restart symantec DLP


## Option 2: Manual Vendor Product by source Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-symantec_dlp.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-symantec_dlp[sc4s-vps] {
 filter {      
        #netmask(169.254.100.1/24)
        #host("-esx-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('symantec')
            product('dlp')
        ); 
    };   
};

```
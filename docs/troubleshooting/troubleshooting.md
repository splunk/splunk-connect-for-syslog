#Troubleshooting Splunk Connect for Syslog

## HEC/token connection errors (AKA “No data in Splunk”)

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

## Timezone mismatch in events
By default, SC4S resolves the timezone to GMT. If customer have a preference to use local TZ then set the user TZ preference in Splunk during search time rather than at index time. 
[Timezone config documentation](https://docs.splunk.com/Documentation/Splunk/8.0.4/Data/ApplyTimezoneOffsetstotimestamps)


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

For issues with SC4S server. Check SC4S server issues section. To file issues visit [Github Issues](https://github.com/splunk/splunk-connect-for-syslog/issues.)
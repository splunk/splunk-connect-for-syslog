# Splunk Connect for Syslog (SC4S) Frequently Asked Questions

**Q: The universal forwarder with file-based architecture has been the documented Splunk best practice for a long time. Why should I switch to an HTTP Event Collector (HEC) based architecture?**

A:

* Using HEC to stream events directly to the indexers provides superior load balancing, and has shown to produce more even data distribution across the indexers. This even distribution results in significantly enhanced search performance. This benefit is especially valuable in large Splunk deployments.

* The HEC architecture designed in SC4S is also easier to administer with newer versions of syslog-ng. There are fewer opportunities for configuration errors, resulting in higher overall performance.

* HEC, and in particular the “/event” endpoint, offers the opportunity for a far richer data stream to Splunk, with lower resource utilization at ingest time. This rich data stream can be taken advantage of in next-generation add-ons. 

**Q: Is the Splunk HTTP Event Collector (HEC) as reliable as the Splunk universal forwarder?**

A: HEC utilizes standard HTTP mechanisms to confirm that the endpoint is responsive before sending data. The HEC architecture allows you to use an industry standard load balancer between SC4S and the indexer or the included load balancing capability built into SC4S itself.

**Q: What if my team doesn’t know how to manage containers?**

A: Using a runtime like Podman to deploy and manage SC4S containers is exceptionally easy even for those with no prior “container experience”. Our application of container technology behaves much like a packaging system. The interaction uses “systemctl” commands a Linux admin would use for other common administration activities. The best approach is to try it out in a lab to see what the experience is like for yourself!

**Q: Can my team use SC4S with Windows?**

A: You can now run Docker on Windows! Microsoft has introduced public preview technology for Linux containers on Windows. Alternatively, a minimal Centos/Ubuntu Linux VM running on Windows hyper-v is a reliable production-grade choice. 

**Q: My company has the traditional universal forwarder and files-based syslog architecture deployed and running, should I rip and replace a working installation with SC4S?**

A: Generally speaking, if a deployment is working and you are happy with it, it’s best to leave it as is until there is need for major deployment changes, such as scaling your configuration. The search performance improvements from better data distribution is one benefit, so if Splunk users have complained about search performance or you are curious about the possible performance gains, we recommend doing an analysis of the data distribution across the indexers.

**Q: What is the best way to migrate to SC4S from an existing syslog architecture?**

A: When exploring migration to SC4S we strongly recommend that you experiment in a lab prior to deployment to production. There are a couple of approaches to consider: 

* The following approach may result in the fewest duplicate events in Splunk versus other options. In some large or complex environments this may not be feasible however:
  1. Configure the new SC4S infrastructure for all your sources.
  2. Confirm all the sourcetypes are being indexed as expected
  3. Stop the existing syslog servers.

* You can also start with the sources currently sending events on port 514 (the default):
  1. Stand up the new SC4S infrastructure in its default configuration.
  2. Confirm that all the sourcetypes are being indexed as expected.
  3. Retire the old syslog servers listening on port 514.
  4. Once the 514 sources are complete, migrate any other sources. To do this, configure SC4S filters to explicitly identify them either through a unique port, hostID, or CIDR block.
  6. Once you confirm that each sourcetype is successfully indexed, disable the old syslog configurations for that source. 

**Q: How can SC4S be deployed to provide high availability?**

A: The syslog protocol was not designed with HA as a goal, so configuration can be challenging. See [Performant AND Reliable Syslog UDP is best](https://www.rfaircloth.com/2020/05/21/performant-and-reliable-syslog-udp-is-best/) for an excellent overview of this topic.

The syslog protocol limits the extent to which you can make any syslog collection architecture HA; at best it can be made "mostly available". To do this, keep it simple and use OS clustering (shared IP) or even just VMs with vMotion. This simple architecture will encounter far less data loss over time than more complicated schemes. Another possible option is containerization HA schemes for SC4S (centered around MicroK8s) that will take some of the administrative burden of clustering away, but still functions as OS clustering under the hood.

**Q: I’m worried about data loss if SC4S goes down. Could I feed syslog to redundant SC4S servers to provide HA, without creating duplicate events in Splunk?**

A: In many system design decisions there is some level of compromise. Any network protocol that doesn't have an application level ACK will lose data because speed is selected over reliability in the design. This is the case with syslog. Use a clustered IP with an active/passive node for a level of resilience while keeping complexity to a minimum. 
It could be possible to implement a far more complex solution utilizing an additional intermediary technology like Kafka, however the costs may outweigh the real world benefits.

**Q: Can the SC4S container be deployed using OpenShift or Kubernetes?**

A: OpenShift doesn't actually use Podman, it uses a library to wrap OCI that Podman also uses. this wrapper around the wrapper has some shortcomings that prevent the service definitions SC4S requires. There are a number of reasons that OpenShift/K8s are not a good fit for syslog, SNMP or SIP: 
* They can't use UDP and TCP on the same port which breaks multiple Bluecoat and Cisco feeds among others.
* Layered networking shrinks the maximum UDP message which causes data loss due to truncation and drops.
* Long lived TCP connections cause well known problems

**Q: If the XL reference HW can handle just under 1 terabyte per day, how can SC4S be scaled to handle large deployments of many terabytes per day?**

A: SC4S is a distributed architecture. SC4S instances should be deployed in the same VLAN as the source devices. This means that each SC4S instance will only see a subset of the total syslog traffic in a large deployment. Even in a deployment of 100 terabytes or greater, the individual SC4S instances will see loads in gigabytes per day rather than terabyters per day.

**Q: How are security vulnerabilities handled with SC4S?**

A: SC4S is comprised of several components including RHL, Syslog-ng and temporized configurations. If a vulnerability is found in the SC4S configurations, the vulnerabilities are given a critical priority in the Development queue. If vulnerabilities are identified in the third party components (RHL, Syslog-ng, etc.) the fixed versions will be pulled in upon the next SC4S release. Fixed security issues are identified by “[security]” in the SC4S release notes.

**Q: SC4S is being blocked by `fapolicyd`, how do I fix that?**
Create a rule that allows running SC4S in `fapolicyd` configuration:
* Create the file `/etc/fapolicyd/rules.d/15-sc4s.rules`.
* Edit the file to add: `allow perm=open exe=/ : dir=/usr/lib64/ all trust=1`.
* Run `fagenrules --load` to load the new rule.
* Run `systemctl restart fapolicyd` to restart the process.
* Start `sc4s systemctl start sc4s` and verify that there are no errors `systemctl status sc4s`.

**Q: I am facing a unique issue that my postfilter configuration is not working although I don't have any postfilter for the mentioned source?**

A: There may be a OOB postfilter for the source which will be applied, validate this by checking the value of `sc4s_tags` in Splunk. To resolve this, see
`[sc4s-finalfilter]`. Do not use this resolution in any other situation as it can add the cost of the data processing.

**Q: Where should the configuration for the vendors be placed? There are folders of app-parsers and  directories. Which one to use? Does this also mean that csv files for metadata are no longer required?**

A: The configuration for vendors should be placed in `/opt/sc4s/local/config/*/.conf`.
Most of the folders are placeholders, the configuration will work in any of these folders with a `.conf` extension.<br/>
CSV should be placed in `local/context/*.csv`. Using `splunk_metadata.csv` is good for metadata override, but use `.conf` file for everything else in place of other csv files.

**Q: Can we have a file in which we can create all default indexes in one effort?**

A: Refer to [indexes.conf](./resources/indexes.conf), which contains all indexes being created in one effort. This file also has `lastChanceIndex` configured, to use if it fits your requirements.
For more information on this file, please refer [Splunk docs](https://docs.splunk.com/Documentation/Splunk/latest/admin/Indexesconf).

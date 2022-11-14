# Splunk Connect for Syslog (SC4S) Frequently Asked Questions

**Q: The Universal Forwarder/files based architecture has been the documented Splunk best practice for a long time.  Why switch to a HTTP Event Collector (HEC) based architecture?**

A: Using HEC to stream events directly to the Indexers provides superior load balancing which has shown to produce dramatically more even data distribution across the Indexers. This even distribution results in significantly enhanced search performance. This benefit is especially valuable in large Splunk deployments.

The HEC architecture designed into SC4S is also far easier to administer with newer versions of syslog-ng, which SC4S takes advantage of.  There are far fewer opportunities for mis-configuration, resulting in higher overall performance and customer adoption.

Lastly, HEC (and in particular, the “/event” endpoint) offers the opportunity for a far richer data stream to Splunk, with lower resource utilization at ingest.  This rich data stream can be taken advantage of in next-generation TAs. 

**Q: Is the Splunk HTTP Event Collector (HEC) as reliable as the Splunk Universal Forwarder?**

A: HEC utilizes standard HTTP mechanisms to confirm that the endpoint is responsive before sending data. The HEC architecture allows for the use of an industry standard load balancer between SC4S and the Indexer, or the included load balancing capability built into SC4S itself.

**Q: What if my team doesn’t know how to manage containers?**

A: SC4S supports both container-based and “bring-your-own-environment” (BYOE) deployment methods. That said, using a runtime like Podman to deploy and manage SC4S containers is exceptionally easy even for those with no prior “container experience”. Our application of container technology behaves much like a packaging system. The interaction is mostly via “systemctl” commands a Linux admin would use for other common administration activities. The best approach is to try it out in a lab to see what the experience is like for yourself!

BYOE is intended for advanced deployments that can not use the Splunk container for some reason. One possible reason is a need to “fork” SC4S in order to implement heavy bespoke customization. Though many will initially gravitate toward BYOE because managing config files and syslog-ng directly is “what they know”, most enterprises will have the best experience using the container approach.

**Q: Can my team use SC4S if we are Windows only shop?**

A: You can now run Docker on Windows! Microsoft has introduced public preview technology for Linux containers on Windows. Alternatively, a minimal Centos/Ubuntu Linux VM running on Windows hyper-v is a reliable production-grade choice. 

**Q: My company has the traditional UF/files based syslog architecture deployed and running, should I rip/replace a working installation with SC4S?**

A: Generally speaking, if a deployment is working and you are happy with it, it’s best to leave it as is until there is need for major deployment changes such as higher scale. That said, the search performance gains realized from better data distribution is a benefit not to be overlooked. If Splunk users have complained about search performance or you are curious about the possible performance gains, we recommend doing an analysis of the data distribution across the indexers.

It may make sense to upgrade to SC4S if there is a change in administration as well.  Properly architecting a performant UF/files syslog-ng deployment is difficult, and an administrative personnel change offers the opportunity to “make a break”  to SC4S, where a new set of administrators would otherwise be tasked with understanding the existing (likely complicated) architecture.

**Q: What is the best way to migrate to SC4S from an existing syslog architecture?**

A: When exploring migration to SC4S we strongly recommend experimentation in a lab prior to deployment to production. There are a couple of approaches to consider: 

One option is to stand up and configure the new SC4S infrastructure for all your sources, then confirm all the sourcetypes are being indexed as expected, and finally stop the existing syslog servers. This big bang approach may result in the fewest duplicate events in Splunk vs other options. In some large or complex environments this may not be feasible however. 

A second option is to start with the sources currently sending events on port 514 (the default). In this case you would stand up the new SC4S infrastructure in its default configuration, confirm all the sourcetypes are being indexed as expected, then retire the old syslog servers listening on port 514. Once the 514 sources are complete you can move on to migrating any other sources one by one. To migrate these other sources you would configure SC4S filters to explicitly identify them either via unique port, hostID or CIDR block. Again, once you confirm that each sourcetype is successfully being indexed then you may disable the old syslog configurations for that source. 

**Q: How can SC4S be deployed to provide high availability?**

A: It is challenging to provide HA for syslog because the syslog protocol itself was not designed with HA as a goal. See [Performant AND Reliable Syslog UDP is best](https://www.rfaircloth.com/2020/05/21/performant-and-reliable-syslog-udp-is-best/) for an excellent overview of this topic.

The gist is that the protocol itself limits the extent to which you can make any syslog collection architecture HA; at best it can be made "mostly available".  Think of syslog as MP3 -- it is a "lossy" protocol and there is nothing you can do to restore it to CD quality (lossless). Some have attempted to implement HA via front-side load balancers; please don’t!  This is the most common architectural mistake folks make when architecting large-scale syslog data collection. So -- how to make it "mostly available"?  Keep it simple, and use OS clustering (shared IP) or even just VMs with vMotion.  This simple architecture will encounter far less data loss over time than more complicated schemes. Another possible option being evaluated is containerization HA schemes for SC4S (centered around microk8s) that will take some of the admin burden of clustering away -- but it is still OS clustering under the hood.

**Q: I’m worried about data loss if SC4S goes down. Could I feed syslog to redundant SC4S servers to provide HA, without creating duplicate events in Splunk?**

A: In many/most system design decisions there is some level of compromise. Any network protocol that doesn't have an application level ack will lose data, as speed was selected over reliability in the design, this is the case with syslog. Use of a clustered IP with an active/passive node will however offer a level of resilience while keeping complexity to a minimum. 
It could be possible to implement a far more complex solution utilizing an additional intermediary technology like Kafka, however the costs may outweigh the real world benefits.

**Q: Can the SC4S container be deployed using OpenShift or K8s?**

A: There are a number of reasons that OpenShift/K8s are not a good fit for syslog, SNMP or SIP. They can't use UDP and TCP on the same port which breaks multiple Bluecoat and Cisco feeds among others.
Layered networking shrinks the maximum UDP message which causes data loss due to truncation and drops
Long lived TCP connections cause well known problems
OpenShift doesn't actually use Podman, it uses a library to wrap OCI that Podman also uses. this wrapper around the wrapper has some shortcomings that prevent the service definitions SC4S requires.
Basically, K8s was built for a very different set of problems than syslog

**Q: If the XL reference HW can handle just under 1 TB/day how can SC4S be scaled to handle large deployments of many TB/day?**

A: SC4S is a distributed architecture. SC4S instances should be deployed in the same VLAN as the source devices. This means that each SC4S instance will only see a subset of the total syslog traffic in a large deployment. Even in a 100+ TB deployment the individual SC4S instances will see loads in GB/day not TB/day.

**Q: How are security vulnerabilities handled with SC4S?**

A: SC4S is comprised of several components including RHL, Syslog-ng and temporized configurations. If a vulnerability is found in the SC4S configurations, they will be given a critical priority in the Development queue. If vulnerabilities are identified in the third party components (RHL, Syslog-ng, etc.) the fixed versions will be pulled in upon the next SC4S release. Fixed security issues are identified by “[security]” in SC4S release notes.

**Q: SC4S is being blocked by `fapolicyd`, how do I fix that?**
Create a rule that allows running sc4s in fapolicyd configuration:
* Create the file `/etc/fapolicyd/rules.d/15-sc4s.rules` .
* Put this into the file: `allow perm=open exe=/ : dir=/usr/lib64/ all trust=1` .
* Run `fagenrules --load` to load the new rule.
* Run `systemctl restart fapolicyd` to restart the process.
* Start `sc4s systemctl start sc4s` and verify there are no errors systemctl status sc4s.

**Q: I am facing a unique issue that my postfilter configuration is not working although i don't have any postfilter for the mentioned source?**

A: There is a possibility that there is OOB postfilter for the source which will be applied , the same can be validated by checking the value of sc4s_tags in splunk UI, to fix this Please use a new topic called
`[sc4s-finalfilter]`  **please don't use it in any other case as it can add the cost of the processing of data**

**Q: Where the config for the vendors should be placed? There are folders of app-parsers and its directories. Which one to use?<br/>
Does this also mean that csv files for metadata are no longer required?**

A: It should be placed inside `/opt/sc4s/local/config/*/.conf`.
Most of the folders are placeholder and it will work in any of these folders if it has **.conf** extension.<br/>
It is required but it should be placed in `local/context/*.csv`. Using **splunk_metadata.csv** is good for metadata override but it is recommended to use .conf file for everything else in place of other csv files.

**Q: Can we have a file using which we can create all default indexes in one go?**

A: Refer this [file](./resources/indexes.conf) which contains all indexes being created in one go.<br/>
Also, above file has **lastChanceIndex** configured, please use it only if it fits your requirement. If not, then please discard the use of lastChanceIndex.<br/>
For more information on this file, please refer [Splunk docs](https://docs.splunk.com/Documentation/Splunk/latest/admin/Indexesconf).

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

**Q: I’m worried about data loss if SC4S goes down. Could I feed syslog to redundant SC4S servers to provide HA, without creating duplicate events in Splunk?**

A: In many/most system design decisions there is some level of compromise. Any network protocol that doesn't have an application level ack will lose data, as speed was selected over reliability in the design, this is the case with syslog. Use of a clustered IP with an active/passive node will however offer a level of resilience while keeping complexity to a minimum. 
It could be possible to implement a far more complex solution utilizing an additional intermediary technology like Kafka, however the costs may outweigh the real world benefits.



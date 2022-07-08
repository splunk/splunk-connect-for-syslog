# Welcome to Splunk Connect for Syslog!

Splunk Connect for Syslog is an open source packaged solution for 
getting data into Splunk.  It is based on the syslog-ng Open Source Edition (Syslog-NG OSE) and transports data to Splunk via the Splunk 
HTTP event Collector (HEC) rather than writing events to disk for collection by a Universal Forwarder.

## Product Goals

* Bring a tested configuration and build of syslog-ng OSE to the market that will function consistently regardless of the underlying host's linux distribution
* Provide a container with the tested configuration for Docker/K8s that can be more easily deployed than upstream packages directly on a customer OS
* Provide validated (testable and tested) implementations of filter and parse functions for common vendor products
* Reduce latency and improve scale by balancing event distribution across Splunk Indexers


## Support

* Splunk Connect for Syslog is an open source project that is now officially supported by Splunk.  That said, the notes below outlining community support are still highly relevant.

Splunk Connect for Syslog is an open source product developed by Splunkers with contributions from the community of partners and customers.
This unique product will be enhanced, maintained and supported by the community, led by Splunkers with deep subject matter expertise. The
primary reason why Splunk is taking this approach is to push product development closer to those that use and depend upon it. This direct
connection will help us all be more successful and move at a rapid pace.

Post a question to Splunk Answers using the tag "Splunk Connect For Syslog"

Join the #splunk-connect-for-syslog room in the splunk-usergroups Slack Workspace. If you don't yet have an account [sign up](https://docs.splunk.com/Documentation/Community/1.0/community/Chat)

**Please use the GitHub issue tracker to submit bugs or request enhancements: https://github.com/splunk/splunk-connect-for-syslog/issues**

Get involved, try it out, ask questions, contribute filters, and make new friends!

## Contributing

We welcome feedback and contributions from the community! Please see our [contribution guidelines](CONTRIBUTING.md) for more information on how to get involved.

## License

* Configuration and documentation licensed subject to [CC0](LICENSE-CC0)

* Code and scripts licensed subject to [BSD-2-Clause](LICENSE-BSD2) 

* Third Party Red Hat Universal Base Image see [License](https://www.redhat.com/licenses/EULA_Red_Hat_Universal_Base_Image_English_20190422.pdf)

* Third Party Syslog-NG (OSE) [License](https://github.com/balabit/syslog-ng)

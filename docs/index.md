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

**Splunk Support**: If you are an existing Splunk customer with access to the Support Portal, create a support ticket for the quickest resolution to any issues you experience. Here are some examples of when it may be appropriate to create a support ticket:
- If you experience an issue with the current version of SC4S, such as a feature gap or a documented feature that is not working as expected.
- If you have difficulty with the configuration of SC4S, either at the back end or with the out-of-box parsers or index configurations.
- If you experience performance issues and need help understanding the bottlenecks.
- If you have any questions or issues with the SC4S documentation.

**GitHub Issues**: For all enhancement requests, please feel free to create GitHub issues. We prioritize and work on issues based on their priority and resource availability. You can help us by tagging the requests with the appropriate labels. 

_Splunk Developers are active in the external usergroup on best effort basis, please use support case/github issues to resolve your issues quickly_


## Contributing

We welcome feedback and contributions from the community! Please see our [contribution guidelines](CONTRIBUTING.md) for more information on how to get involved.

## License

* Configuration and documentation licensed subject to [CC0](LICENSE-CC0)

* Code and scripts licensed subject to [BSD-2-Clause](LICENSE-BSD2) 

* Third Party Axoflow image of syslog-ng [License](https://github.com/axoflow/axosyslog-docker/blob/main/LICENSE.)

* Third Party Syslog-NG (OSE) [License](https://github.com/balabit/syslog-ng)

## References

* Syslog-ng Documentation provided by Axoflow [Docs](https://axoflow.com/docs/axosyslog/)

# README
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog?ref=badge_shield)


Splunk Connect for Syslog is an open source packaged solution to 
get data into Splunk using syslog-ng (OSE) and the Splunk 
HTTP event Collector. 

## Purpose

Splunk Connect for Syslog (SC4S) is a community project that helps reduce the pain of getting syslog data sources into Splunk. Splunk Connect for Syslog should be used by any Splunk customer needing to onboard data sources via syslog to Splunk. The primary pain points SC4S addresses include the following:

* Lack of deep syslog expertise in the community
* Inconsistency between syslog server deployments, which creates a support challenge
* Data sources tagged with catch-all sourcetype “syslog”, which limits Splunk analytics
* Uneven data distribution between Splunk indexers, which impacts search performance


## Usage

For full usage instructions, please visit the Splunk Connect for Syslog [documentation](https://splunk.github.io/splunk-connect-for-syslog/).

## Getting Support

Thank you for considering SC4S for your Splunk needs.

**Splunk Support**: If you are an existing Splunk customer with access to the Support Portal, create a support ticket for the quickest resolution to any issues you experience. Here are some examples of when it may be appropriate to create a support ticket:
- If you experience an issue with the current version of SC4S, such as a feature gap or a documented feature that is not working as expected.
- If you have difficulty with the configuration of SC4S, either at the back end or with the out-of-box parsers or index configurations.
- If you experience performance issues and need help understanding the bottlenecks.
- If you have any questions or issues with the SC4S documentation.

**GitHub Issues**: For all enhancement requests, please feel free to create GitHub issues. We prioritize and work on issues based on their priority and resource availability. You can help us by tagging the requests with the appropriate labels. 

_Splunk Developers are active in the external usergroup on best effort basis, Please use support case/github issues to resolve your issues quickly_


## Contributing

We welcome feedback and contributions from the community! Please see our [contribution guidelines](/docs/CONTRIBUTING.md) for more information on how to get involved. PR contributions require acceptance of both the code of conduct and the contributor license agreement.

This repository uses `pre-commit`. After installing dependencies, please do
```bash
pre-commit install
```

## License

* Configuration and documentation licensed subject to [CC0](LICENSE-CC0)

* Code and scripts licensed subject to [BSD-2-Clause](LICENSE-BSD2) 

* Third Party Axoflow image of syslog-ng [License](https://github.com/axoflow/axosyslog-docker/blob/main/LICENSE.)

* Third Party Syslog-NG (OSE) [License](https://github.com/balabit/syslog-ng)


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog?ref=badge_large)

## References

* Syslog-ng Documentation provided by Axoflow [Docs](https://axoflow.com/docs/axosyslog/)

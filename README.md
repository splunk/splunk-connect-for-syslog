# README
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog?ref=badge_shield)


Splunk Connect for Syslog is an open source packaged solution for 
getting data into Splunk using syslog-ng (OSE) and the Splunk 
HTTP event Collector. 

## Purpose

Splunk Connect for Syslog (SC4S) is a community project focused on reducing the pain of getting syslog data sources into Splunk. The primary pain points SC4S addresses include the following…

* Shortage of deep syslog expertise in the community
* Inconsistency between syslog server deployments creates a support challenge
* Data sources tagged with catch-all sourcetype “syslog” which limits Splunk analytics
* Uneven data distribution between Splunk indexers impacts search performance
* Splunk Connect for Syslog should be used by any Splunk customer needing to onboard data sources via syslog to Splunk.

## Usage

For full usage instructions, please visit the Splunk Connect for Syslog [documentation](https://splunk.github.io/splunk-connect-for-syslog/).

## Getting Support

Thank you for considering SC4S for your Splunk needs.
1) Splunk Support: If you are an existing Splunk customer with access to the Support Portal, create a support ticket for the quickest resolution to any issues you may be experiencing. Here are some examples of when it may be appropriate to create a support ticket:
If you experience an issue with the current version of SC4S, such as a feature gap or a documented feature that is not working as expected.
If you have difficulty with the configuration of SC4S, either at the back end or with the out-of-box parsers or index configurations.
If you experience performance issues and need help understanding the bottlenecks.
If you have any questions or issues with the SC4S documentation.
2) Community Support: Community members are often a great source of support and knowledge. We also invite you to help others.
 Here are some ways in which community support can be involved. 
Post a question to Splunk Answers using the tag "Splunk Connect For Syslog"
Join the #splunk-connect-for-syslog room in the splunk-usergroups Slack Workspace. If you don't yet have an account, you can sign up.
Please use the GitHub issue tracker to submit bugs or request enhancements: https://github.com/splunk/splunk-connect-for-syslog/issues

Please note that the Splunk team is involved as much as possible in the community, on a best effort basis. If you require priority handling, please use Splunk Support.


## Contributing

We welcome feedback and contributions from the community! Please see our [contribution guidelines](/docs/CONTRIBUTING.md) for more information on how to get involved. PR contributions require acceptance of both the code of conduct and the contributor license agreement.

This repository uses `pre-commit`. After installing dependencies, please do
```bash
pre-commit install
```

## License

* Configuration and documentation licensed subject to [CC0](LICENSE-CC0)

* Code and scripts licensed subject to [BSD-2-Clause](LICENSE-BSD2) 

* Third Party Red Hat Universal Base Image see [License](https://www.redhat.com/licenses/EULA_Red_Hat_Universal_Base_Image_English_20190422.pdf)

* Third Party Syslog-NG (OSE) [License](https://github.com/balabit/syslog-ng)


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fsplunk%2Fsplunk-connect-for-syslog?ref=badge_large)
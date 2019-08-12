# Welcome to Splunk Connect for Syslog

Splunk Connect for Syslog is an open source packaged solution for 
getting data into Splunk using syslog-ng open source edition (Syslog-NG OSE) and the Splunk 
HTTP event Collector. 

## Project Goals

* Bring a tested configuration and build of syslog-ng OSE to the market that will function consistently regardless of the underlying host's linux distribution
* Provide a container with the tested configuration for Docker/K8s that can be more easily deployed than upstream packages directly on a customer OS
* Provide validated (testable and tested) implementations of filter and parse functions for common vendor products
* Reduce latency and improve scale by balancing event distribution across Splunk Indexers



## License

* Configuration and documentation licensed subject to [CC0](LICENSE-CC0)

* Code and scripts licensed subject to [BSD-2-Clause](LICENSE-BSD2) 

* Third Party Red Hat Universal Base Image see [License](https://www.redhat.com/licenses/EULA_Red_Hat_Universal_Base_Image_English_20190422.pdf)

* Third Party Syslog-NG (OSE) [License](https://github.com/balabit/syslog-ng)

# SC4S Enterprise

## End of Support

**Important:** The SC4S Enterprise will reach End of Support on April 1, 2026. After that date, this repository will no longer receive updates from Splunk and will no longer be supported by Splunk.

## About SC4S Enterprise
Introducing SC4S Enterprise, a robust and reliable solution crafted for organizations that prioritize stability over frequent updates. This release represents a shift towards predictable, stable, and streamlined software development, focusing on delivering a high-quality experience with fewer, carefully curated updates,this is initial version of the product, next version will be more matured with feature, patches and removal of experimental feature

##  Release Cycle
1. Patch Release: Quarterly
2. Version Update: Annualy



## Security considerations
SC4S Enterprise is built on an Alpine lightweight container which has very little vulnerability. SC4S Enterprise supports secure syslog data transmission protocols such as RELP and TLS over TCP to protect your data in transit. 


## Implement SC4S Enterprise
To implementat of SC4S Enterprise:

1. Set up the SC4S Enterprise environment.
2. Install SC4S Enterprise following the [instructions for your chosen environment](../gettingstarted/) except microk8s and Kubernetes with the following changes:

* In the service file for Podman or Docker replace references of standard container image (`container2` or `container3`) with `enterprise`.


3. Configure source systems to send syslog data to SC4S Enterprise.
4. Test the setup to ensure that your syslog data is correctly received, processed, and forwarded to Splunk.

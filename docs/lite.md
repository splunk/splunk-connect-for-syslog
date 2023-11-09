# SC4S Lite
## Purpose
SC4S Lite has been designed to provide a scalable, performance-oriented solution for syslog data ingestion into Splunk. 
The addition of Pluggable Modular Parsers offers users the flexibility to incorporate custom data processing logic to suit specific use cases.
## Architecture
![architecture diagram](sc4slite_arch_diag.png)

## Components and Modules

### SC4S Lite
The primary component of the system, SC4S Lite is built upon the SC4S, providing a lightweight, high-performance sc4s  solution, the current SC4S is very complex and packed with too many oob parser support.

### Pluggable Modules
Pluggable modules it's **predefined modules**, that you can **only** enable/disable (can't create or update modulew) by changing config file.
Each pluggable module representing set of parsers for each vendor that supporting SC4S.

[More detail guide here](pluggable_modules.md)

### Splunk Enterprise or Splunk Cloud
The Splunk platform is the destination for the syslog data. Splunk allows for comprehensive analysis, searching, and visualization of the processed data.

##  Data Flow
Source systems send syslog data to SC4S Lite. The data may be transmitted via UDP, TCP, or RELP, depending on the system's capabilities and configurations.
SC4S Lite receives the syslog data and routes it through the appropriate parsers, as defined by user configurations.
The parsers in pluggable module process the data, including parsing, filtering, and enriching the data with metadata.
SC4S Lite forwards the processed syslog data to the Splunk platform over the HTTP Event Collector (HEC).

## Security Considerations
SC4S Lite is built on an alpine lightweight container which has very little vulnerability as well as it  supports secure syslog data transmission protocols (such as RELP and TLS over TCP) to protect the data in transit. Furthermore, the environment in which SC4S Lite is deployed enhances data security.

## Scalability and Performance
SC4S Lite is designed to provide superior performance and scalability, thanks to the lightweight architecture and pluggable parsers, which distribute the processing load. It is also packed with ebpf program which can further enhance the performance.
Note: The actual performance may depend on factors such as the server capacity and network bandwidth.

## Implementation Plan
The implementation of SC4S Lite involves several steps, including:


- Setting up the SC4S Lite environment.
- Installing sc4s lite version following the [instruction chosen environment](./gettingstarted/). 

  NOTE: In the service file (for podman or docker) replace references of standard container image (`container2` or `container3`) with `container3lite`. For microk8s replace reference to standard image in `values.yaml` file.
- Configuring source systems to send syslog data to SC4S Lite.
- Developing and integrating custom parsers as per specific needs.
- Configuring SC4S Lite to route syslog data through appropriate parsers and forward to Splunk.
- Testing the setup to ensure syslog data is correctly received, processed, and forwarded to Splunk.

# SC4S Lite
## Purpose
SC4S Lite has been designed to provide a scalable, performance-oriented solution for syslog data ingestion into Splunk. 
The addition of Pluggable Modular Parsers offers users the flexibility to incorporate custom data processing logic to suit specific use cases.
## Architecture
![architecture diagram](sc4slite_arch_diag.png)

## Components and Modules

### SC4S Lite
The primary component of the system, SC4S Lite is built upon the SC4S, providing a lightweight, high-performance sc4s  solution, the current SC4S is very complex and packed with too many oob parser support.

### Pluggable Modular Parsers
The Pluggable Modular Parsers provide the ability to customize and extend the data processing logic of SC4S Lite. Users can create and integrate custom parsers to suit their specific needs, enhancing the flexibility of data processing.

### Splunk Enterprise or Splunk Cloud
SC4S sends your syslog data to the Splunk platform where you can perform comprehensive analysis, searching, and visualization of the processed data.

##  Data Flow
Source systems send syslog data to SC4S Lite through UDP or TCP, depending on your system's capabilities and configurations.
SC4S Lite receives the syslog data and routes it through the parsers defined by your configurations. These parsers in the plugin module process the data, includig parsing, filtering, and enriching the data with metadata.
SC4S Lite forwards the processed syslog data to the Splunk platform over the HTTP Event Collector (HEC).

## Security Considerations
SC4S Lite provides superior performance and scalability by implementing lightweight architecture and pluggable parsers that distribute the processing load. It is also packaged with an eBPF program to help further enhance performance.

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

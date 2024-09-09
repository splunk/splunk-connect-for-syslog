# Nginx Open Source

This section of the documentation describes the challenges of load balancing syslog traffic using Nginx Open Source.

There are several key disadvantages to using Nginx Open Source for this purpose:
- Nginx Open Source does not provide active health checking, which is essential for UDP DSR (Direct Server Return) load balancing.
- Even with round-robin load balancing, traffic distribution can often be uneven, leading to overloaded instances in the pool. This results in growing queues, causing delays, data drops, and potential memory or disk issues.
- Without High Availability, an Nginx Open Source load balancer becomes a new single point of failure.

**Please note that Splunk only supports SC4S**. If issues arise due to the load balancer, please reach out to the Nginx support team.

## Install Nginx

1. Refer to the Nginx documentation for instructions on installing Nginx **with the stream module**, which is required for TCP/UDP load balancing. For example, on Ubuntu:
```bash
sudo apt update
sudo apt -y install nginx libnginx-mod-stream
```

2. (Optionally) Refer to the Nginx documentation for instructions on fine-tuning Nginx performance. For example, you can update the `events` section in your Nginx configuration file:

`/etc/nginx/nginx.conf`
```conf
events {
    worker_connections 20480;
    multi_accept on;
    use epoll;
}
```
Please note that actual load balancer fine-tuning is beyond the scope of the SC4S team's responsibility.

## Preserving Source IP
The default behavior of Nginx is to overwrite the source IP with the LB's IP. While some users accept this behavior, it is recommended to preserve the original source IP of the message.

Nginx offers three methods to preserve the source IP:

| Method                      | Protocol   |
|-----------------------------|------------|
| PROXY protocol              | TCP*       |
| Transparent IP              | TCP/TLS    |
| Direct Server Return (DSR)  | UDP        |

* TLS PROXY protocol support in SC4S is scheduled for implementation.

Examples for setting up Nginx with the PROXY protocol and DSR are provided below. The Transparent IP method requires complex network configuration. For more details, refer to [this Nginx blog post](https://www.f5.com/company/blog/nginx/ip-transparency-direct-server-return-nginx-plus-transparent-proxy).


## Option 1: Configure Nginx Open Source with the PROXY Protocol

### Advantages:
- Easy to set up

### Disadvantages:
- Available only for TCP, not for UDP or TLS
- Overwriting the source IP in SC4S is not ideal; the `SOURCEIP` is a hard macro and only `HOST` can be overwritten
- Overwriting the source IP is available only in SC4S versions greater than 3.4.0

### Configuration

1. On your load balancer (LB) node, add a configuration similar to the following:
`/etc/nginx/modules-enabled/sc4s.conf`
```conf
stream {
    # Define upstream for each of SC4S hosts and ports
    # Default SC4S TCP ports are 514, 601
    # Include your custom ports if applicable
    upstream stream_syslog_514 {
        server <SC4S_IP_1>:514;
        server <SC4S_IP_2>:514;
    }
    upstream stream_syslog_601 {
        server <SC4S_IP_1>:601;
        server <SC4S_IP_2>:601;
    }

    # Define a common configuration block for all servers
    map $server_port $upstream_name {
        514   stream_syslog_514;
        601   stream_syslog_601;
    }

    # Define a virtual server for each upstream connection
    # Ensure 'proxy_protocol' is set to 'on'
    server {
        listen        514;
        listen        601;
        proxy_pass    $upstream_name;
        
        proxy_timeout 3s;
        proxy_connect_timeout 3s;
        
        proxy_protocol on;
    }
}
```

3. Refer to the Nginx documentation to find the command to reload the service, for example:
```bash
sudo nginx -s reload
```

4. Add the following parameter to the SC4S configuration and restart your instances:
`/opt/sc4s/env_file`
```conf
SC4S_SOURCE_PROXYCONNECT=yes
```

### Test Your Setup
Send TCP messages to the load balancer and verify that they are correctly received in Splunk with the host set to your source IP, not the LB's IP:

```bash
# Test message without IETF frame for port 514/TCP:
echo "hello world" | netcat <LB_IP> 514
# Test message with IETF frame for port 601/TCP:
echo "11 hello world" | netcat <LB_IP> 601
```

3. Run performance tests based on the [Check TCP Performance](tcp_performance_tests.md) section.

| Receiver                  | Performance                    |
|---------------------------|--------------------------------|
| Single SC4S Server         | 4,341,000 (71,738.98 msg/sec)  |
| Load Balancer + 2 Servers  | 5,996,000 (99,089.03 msg/sec)  |

Please note that load balancer fine-tuning is beyond the scope of the SC4S team's responsibility. For assistance in increasing the TCP throughput of your load balancer instance, contact the Nginx support team.

## Option 2: Configure Nginx with DSR (Direct Server Return)

### Advantages:
- Works for UDP
- Saves one hop and additional wrapping

### Disadvantages:
- DSR setup requires active health checks because the load balancer cannot expect responses from the upstream. Active health checks are not available in Nginx Open Source, so switch to Nginx Plus or implement your own active health checking.
- Requires superuser privileges.
- For cloud users, this might require disabling `Source/Destination Checking` (tested with AWS).

1. In the main Nginx configuration, update the `user` to root:
`/etc/nginx/nginx.conf`
```conf
user root;
```

2. Add a configuration similar to the following in:
`/etc/nginx/modules-enabled/sc4s.conf`
```conf
stream {
    # Define upstream for each of SC4S hosts and ports
    # Default SC4S UDP port is 514
    # Include your custom ports if applicable
    upstream stream_syslog_514 {
        server <SC4S_IP_1>:514;
        server <SC4S_IP_2>:514;
    }

    # Define connections to each of your upstreams.
    # Ensure to include `proxy_bind` and `proxy_responses 0`.
    server {
        listen        514 udp;
        proxy_pass    stream_syslog_514;
        
        proxy_bind $remote_addr:$remote_port transparent;
        proxy_responses 0;
    }
}
```

3. Refer to the Nginx documentation to find the command to reload the service, for example:
```bash
sudo nginx -s reload
```

4. Ensure that you disable `Source/Destination Checking` on your load balancer's host if you are working on AWS.

### Test Your Setup
1. Send UDP messages to the load balancer and verify that they are correctly received in Splunk with the correct host IP:
```bash
echo "hello world" > /dev/udp/<LB_IP>/514
```

2. Run performance tests

| Receiver / Drops Rate for EPS (msgs/sec) | 4,500  | 9,000  | 27,000 | 50,000 | 150,000 | 300,000 |
|------------------------------------------|--------|--------|--------|--------|---------|---------|
| Single SC4S Server                       | 0.33%  | 1.24%  | 52.31% | 74.71% |    --   |    --   |
| Load Balancer + 2 Servers                | 1%     | 1.19%  | 6.11%  | 47.64% |    --   |    --   |
| Single Finetuned SC4S Server             | 0%     | 0%     | 0%     | 0%     |  47.37% |    --   |
| Load Balancer + 2 Finetuned Servers      | 0.98%  | 1.14%  | 1.05%  | 1.16%  |  3.56%  |  55.54% |

Please note that load balancer fine-tuning is beyond the scope of the SC4S team's responsibility. For assistance in minimizing UDP drops on the load balancer side, contact the Nginx support team.
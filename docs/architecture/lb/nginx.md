# NGINX

If you choose NGINX as a solution, consider the following when using it to scaling syslog ingestion:

- **Uneven TCP traffic distribution**: Even with round-robin load balancing, TCP traffic may not be evenly distributed, leading to overloaded instances. This can cause growing queues, delays, data loss, and potential memory or disk issues.
  
- **UDP limitations**: UDP is a protocol prone to data loss, and load balancers can introduce another point of data loss.
  
- **Lack of active health checking**: NGINX Open Source does not provide active health checking, which is important for UDP Direct Server Return (DSR) load balancing. NGINX Plus offers active health checking with a paid license.
  
- **No built-in High Availability (HA)**: NGINX Open Source lacks native support for High Availability. Without HA, your NGINX load balancer becomes a single point of failure. NGINX Plus includes built-in HA support as part of the paid offering.

**Please note that Splunk only supports SC4S**. If issues arise due to the load balancer, please reach out to the NGINX support team.

## Install NGINX Open Source

Refer to the NGINX documentation to install NGINX **with the stream module**, which is required for TCP/UDP load balancing. For example, on Ubuntu:
```bash
sudo apt update
sudo apt -y install nginx libnginx-mod-stream
```

## Install NGINX Plus

See your NGINX documentation for information about licenses and installation. For example, on Ubuntu:
```bash
sudo mkdir -p /etc/ssl/nginx

sudo apt update
sudo apt-get install apt-transport-https lsb-release ca-certificates wget gnupg2 ubuntu-keyring

# Subscribe to NGINX Plus to obtain nginx-repo.key and nginx-repo.crt
sudo cp nginx-repo.key nginx-repo.crt /etc/ssl/nginx/

wget -qO - https://cs.nginx.com/static/keys/nginx_signing.key | gpg --dearmor | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
printf "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] https://pkgs.nginx.com/plus/ubuntu `lsb_release -cs` nginx-plus\n" | sudo tee /etc/apt/sources.list.d/nginx-plus.list

sudo wget -P /etc/apt/apt.conf.d https://cs.nginx.com/static/files/90pkgs-nginx

sudo apt-get update
sudo apt-get install nginx-plus
```

```bash
nginx -v
```

## Fine-tune NGINX
2. (Optional) See your NGINX documentation for information about fine-tuning NGINX performance. For example, you can update the `events` section in your NGINX configuration file:

`/etc/nginx/nginx.conf`
```conf
events {
    worker_connections 20480;
    multi_accept on;
    use epoll;
}
```
Load balancer support and fine-tuning is outside the scope of the SC4S team's responsibility.

## Preserving source IP
By default, NGINX overwrites the source IP with the load balancer's IP. As a best practice, preserve the original source IP of the message.

NGINX provides three methods to preserve the source IP:

| Method                      | Protocol   |
|-----------------------------|------------|
| PROXY protocol              | TCP*       |
| Transparent IP              | TCP/TLS    |
| Direct Server Return (DSR)  | UDP        |

* TLS PROXY protocol support in SC4S is scheduled for implementation.

Examples for setting up NGINX with the PROXY protocol and DSR are provided below. The Transparent IP method requires complex network configuration. For more details, refer to [this NGINX blog post](https://www.f5.com/company/blog/nginx/ip-transparency-direct-server-return-nginx-plus-transparent-proxy).


## Option 1: Configure NGINX with the PROXY protocol

### Advantages:
- Easy to set up.

### Disadvantages:
- Available only for TCP, not for UDP or TLS.
- Overwriting the source IP in SC4S is not a best practice; the `SOURCEIP` is a hard macro and only `HOST` can be overwritten.
- Overwriting the source IP is available only in SC4S versions greater than 3.31.0.

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

3. Refer to the NGINX documentation to find the command to reload the service, for example:
```bash
sudo nginx -s reload
```

4. Add the following parameter to the SC4S configuration and restart your instances:
`/opt/sc4s/env_file`
```conf
SC4S_SOURCE_PROXYCONNECT=yes
```

### Test your configuration
Send TCP messages to the load balancer and verify that they are correctly received in Splunk with the host set to your source IP:

```bash
# Test message without IETF frame for port 514/TCP:
echo "hello world" | netcat <LB_IP> 514
# Test message with IETF frame for port 601/TCP:
echo "11 hello world" | netcat <LB_IP> 601
```

3. Run performance tests based on the [Check TCP Performance](performance-tests.md#check-your-tcp-performance) section.

| Receiver                   | Performance        |
|----------------------------|--------------------|
| Single SC4S Server         | 71,738.98 msg/sec  |
| Load Balancer + 2 Servers  | 99,089.03 msg/sec  |

Note that load balancer support and fine-tuning is beyond the scope of the SC4S team's responsibility. For assistance in increasing the TCP throughput of your load balancer instance, contact your NGINX support team.

## Option 2: Configure NGINX with DSR (Direct Server Return)

### Advantages:
- Works for UDP
- Reduced latency

### Disadvantages:
- DSR setup requires active health checks because the load balancer cannot expect responses from the upstream. Active health checks are not available in NGINX, so switch to NGINX Plus or implement your own active health checking.
- Requires switching to the `root` user.
- For cloud users, this might require disabling `Source/Destination Checking` (tested with AWS).

1. In the main NGINX configuration, update the `user` to root:
`/etc/nginx/nginx.conf`
```conf
user root;
```

2. Add a configuration similar to the following:

**For NGINX Open Source:**

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
    # Include `proxy_bind` and `proxy_responses 0`.
    server {
        listen        514 udp;
        proxy_pass    stream_syslog_514;
        
        proxy_bind $remote_addr:$remote_port transparent;
        proxy_responses 0;
    }
}
```

**For NGINX Plus:**

- Add the following configuration block to `/etc/nginx/nginx.conf`:
```conf
stream {
    # Define upstream for each of SC4S hosts and ports
    # Default SC4S UDP port is 514
    # Include your custom ports if applicable
    upstream stream_syslog_514 {
        zone   stream_syslog_514 64k;
        server <SC4S_IP_1>:514;
        server <SC4S_IP_2>:514;
    }

    match server_ok {
        send "GET /health HTTP/1.0\r\n\r\n";
        expect ~* '"healthy"';
    }
    
    # Define connections to each of your upstreams.
    # Include `proxy_bind` and `health_check`.
    server {
        listen        514 udp;
        proxy_pass    stream_syslog_514;
        proxy_bind $remote_addr transparent;
        health_check interval=1 match=server_ok port=8080;
    }
}
```

NGINX will actively check the health of your upstream servers by sending UDP messages to port 514.

- (Optional) Add the following local post-filter to each of your SC4S instances to prevent SC4S from forwarding health check messages to Splunk and other destinations:
`/opt/sc4s/local/config/app_parsers/nginx_healthcheck-postfiler.conf`
```conf
block parser nginx_healthcheck-postfiler() {
    channel {
        rewrite(r_set_dest_splunk_null_queue);
    };
};

application nginx_healthcheck-postfiler[sc4s-postfilter] {
    filter {
        "${fields.sc4s_vendor}" eq "splunk" and
        "${fields.sc4s_product}" eq "sc4s"
        and message('nginx health check' type(string));
    };
    parser { nginx_healthcheck-postfiler(); };
};
```

3. Refer to the NGINX documentation to find the command to reload the service, for example:
```bash
sudo nginx -s reload
```

4. Disable `Source/Destination Checking` on your load balancer's host if you are working on AWS.

### Test your configuration
1. Send UDP messages to the load balancer and verify that they are correctly received in Splunk with the correct host IP:
```bash
echo "hello world" > /dev/udp/<LB_IP>/514
```

2. Run performance tests:

| Receiver / Drops Rate for EPS (msgs/sec) | 4,500  | 9,000  | 27,000 | 50,000 | 150,000 | 300,000 |
|------------------------------------------|--------|--------|--------|--------|---------|---------|
| Single SC4S Server                       | 0.33%  | 1.24%  | 52.31% | 74.71% |    --   |    --   |
| Load Balancer + 2 Servers                | 1%     | 1.19%  | 6.11%  | 47.64% |    --   |    --   |
| Single Finetuned SC4S Server             | 0%     | 0%     | 0%     | 0%     |  47.37% |    --   |
| Load Balancer + 2 Finetuned Servers      | 0.98%  | 1.14%  | 1.05%  | 1.16%  |  3.56%  |  55.54% |

Note that load balancer support and fine-tuning is beyond the scope of the SC4S team's responsibility. For assistance in minimizing UDP drops on the load balancer side, contact your NGINX support team.

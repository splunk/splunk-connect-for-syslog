#! /usr/bin/env python3
import os
import jinja2

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

ports = os.getenv(f"SOURCE_ALL_SET")

if os.getenv(f"SC4S_IPV6_ENABLE", "no").lower() in [
    "true",
    "1",
    "t",
    "y",
    "yes",
]:
    enable_ipv6 = "6"
else:
    enable_ipv6 = "4"

if os.getenv(f"SC4S_SOURCE_STORE_RAWMSG", "no").lower() in [
    "true",
    "1",
    "t",
    "y",
    "yes",
]:
    store_raw_message = True
else:
    store_raw_message = False

if os.getenv(f"SC4S_USE_REVERSE_DNS", "no").lower() in [
    "true",
    "1",
    "t",
    "y",
    "yes",
]:
    use_reverse_dns = True
else:
    use_reverse_dns = False

if os.getenv(f"SC4S_SOURCE_TLS_ENABLE", "no").lower() in [
    "true",
    "1",
    "t",
    "y",
    "yes",
]:
    use_tls = True
else:
    use_tls = False

if os.getenv(f"SC4S_RUNTIME_ENV", "unknown").lower() == "k8s":
    cert_file = "tls.crt"
    key_file = "tls.key"
else:
    cert_file = "server.pem"
    key_file = "server.key"


for port_id in ports.split(","):
    outputText = tm.render(
        enable_ipv6=enable_ipv6,
        store_raw_message=store_raw_message,
        port_id=port_id,
        use_reverse_dns=use_reverse_dns,
        use_tls=use_tls,
        tls_dir=os.getenv(f"SC4S_TLS", "/etc/syslog-ng/tls"),
        cert_file=cert_file,
        key_file=key_file,
        topic=os.getenv(f"SC4S_LISTEN_{ port_id }_TOPIC", "sc4s"),
        port_udp=os.getenv(f"SC4S_LISTEN_{ port_id }_UDP_PORT", "disabled").split(","),
        port_udp_sockets=int(os.getenv(f"SC4S_SOURCE_LISTEN_UDP_SOCKETS", 4)),
        port_udp_sorecvbuff=os.getenv(f"SC4S_SOURCE_UDP_SO_RCVBUFF", 17039360),
        port_tcp=os.getenv(f"SC4S_LISTEN_{ port_id }_TCP_PORT", "disabled").split(","),
        port_tcp_sockets=int(os.getenv(f"SC4S_SOURCE_LISTEN_TCP_SOCKETS", 1)),
        port_tcp_max_connections=os.getenv(f"SC4S_SOURCE_TCP_MAX_CONNECTIONS", "2000"),
        port_tcp_log_iw_size=os.getenv(f"SC4S_SOURCE_TCP_IW_SIZE", "20000000"),
        port_tcp_log_fetch_limit=os.getenv(f"SC4S_SOURCE_TCP_FETCH_LIMIT", "2000"),
        port_tcp_so_recvbuff=os.getenv(f"SC4S_SOURCE_TCP_SO_RCVBUFF", "17039360"),
        port_tls=os.getenv(f"SC4S_LISTEN_{ port_id }_TLS_PORT", "disabled").split(","),
        port_tls_sockets=int(os.getenv(f"SC4S_SOURCE_LISTEN_TLS_SOCKETS", 1)),
        port_tls_max_connections=os.getenv(f"SC4S_SOURCE_TLS_MAX_CONNECTIONS", "2000"),
        port_tls_log_iw_size=os.getenv(f"SC4S_SOURCE_TCP_IW_SIZE", "20000000"),
        port_tls_log_fetch_limit=os.getenv(f"SC4S_SOURCE_TCP_FETCH_LIMIT", "2000"),
        port_tls_so_recvbuff=os.getenv(f"SC4S_SOURCE_TLS_SO_RCVBUFF", "17039360"),
        port_tls_tls_options=os.getenv(
            f"SC4S_SOURCE_TLS_OPTIONS", "no-sslv2, no-sslv3, no-tlsv1"
        ),
        port_tls_cipher_suit=os.getenv(
            f"SC4S_SOURCE_TLS_CIPHER_SUITE",
            "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH",
        ),
        port_5426=os.getenv(f"SC4S_LISTEN_{ port_id }_RFC5426_PORT", "disabled").split(
            ","
        ),
        port_5426_sockets=int(os.getenv(f"SC4S_SOURCE_LISTEN_RFC5426_SOCKETS", 1)),
        port_5426_sorecvbuff=os.getenv(f"SC4S_SOURCE_RFC5426_SO_RCVBUFF", 17039360),
        port_6587=os.getenv(f"SC4S_LISTEN_{ port_id }_RFC6587_PORT", "disabled").split(
            ","
        ),
        port_6587_sockets=os.getenv(f"SC4S_SOURCE_LISTEN_RFC6587_SOCKETS", 1),
        port_6587_max_connections=os.getenv(
            f"SC4S_SOURCE_RFC6587_MAX_CONNECTIONS", "2000"
        ),
        port_6587_log_iw_size=os.getenv(f"SC4S_SOURCE_RFC6587_IW_SIZE", "20000000"),
        port_6587_log_fetch_limit=os.getenv(f"SC4S_SOURCE_RFC6587_FETCH_LIMIT", "2000"),
        port_6587_so_recvbuff=os.getenv(f"SC4S_SOURCE_RFC6587_SO_RCVBUFF", "17039360"),
        port_5425=os.getenv(f"SC4S_LISTEN_{ port_id }_RFC5425_PORT", "disabled").split(
            ","
        ),
        port_5425_sockets=int(os.getenv(f"SC4S_SOURCE_LISTEN_RFC5425_SOCKETS", 1)),
        port_5425_max_connections=os.getenv(
            f"SC4S_SOURCE_RFC5425_MAX_CONNECTIONS", "2000"
        ),
        port_5425_log_iw_size=os.getenv(f"SC4S_SOURCE_RFC5425_IW_SIZE", "20000000"),
        port_5425_log_fetch_limit=os.getenv(f"SC4S_SOURCE_RFC5425_FETCH_LIMIT", "2000"),
        port_5425_so_recvbuff=os.getenv(f"SC4S_SOURCE_RFC5425_SO_RCVBUFF", "17039360"),
        port_5425_tls_options=os.getenv(
            f"SC4S_SOURCE_RFC5425_OPTIONS", "no-sslv2, no-sslv3, no-tlsv1"
        ),
        port_5425_cipher_suit=os.getenv(
            f"SC4S_SOURCE_RFC5425_CIPHER_SUITE",
            "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH",
        ),
    )
    print(outputText)

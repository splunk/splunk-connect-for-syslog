source s_dedicated_port_{{.port_id}}{

# ===============================================================================================
# source definition for remote devices
# ===============================================================================================

# ===============================================================================================
# Defaults for the default-network-drivers() source:
# 514, both TCP and UDP, for RFC3164 (BSD-syslog) formatted traffic
# 601 TCP, for RFC5424 (IETF-syslog) formatted traffic
# 6514 TCP, for TLS-encrypted traffic
# ===============================================================================================

    channel {
        source {
{{ if ne (getenv  (print "SC4S_LISTEN_" .port_id "_UDP_PORT" ) "no") "no" }}
# {{ (print "SC4S_LISTEN_" .port_id "_UDP_PORT") }}
            syslog (
                transport("udp")
                port({{getenv  (print "SC4S_LISTEN_" .port_id "_UDP_PORT") }})
                ip-protocol(4)
                so-rcvbuf({{getenv "SC4S_SOURCE_UDP_SO_RCVBUFF" "425984"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(no-parse)
            );
{{ end }}
{{ if ne (getenv  (print "SC4S_LISTEN_" .port_id "_TCP_PORT") "no") "no" }}
# {{ (print "SC4S_LISTEN_" .port_id "_TCP_PORT") }}
            network (
                transport("tcp")
                port({{getenv  (print "SC4S_LISTEN_" .port_id "_TCP_PORT") }})
                ip-protocol(4)
                max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(no-parse)
            );
{{ end }}
        };
        #TODO: #60 Remove this function with enhancement
        rewrite(set_rfcnonconformant);

{{ if eq (getenv "confgen_parser") "rfc5424_strict" }}
        filter(f_rfc5424_strict);
        parser {
                syslog-parser(flags(syslog-protocol  store-raw-message));
            };
        rewrite(set_rfc5424_strict);
{{ else if eq (getenv "confgen_parser") "rfc5424_noversion" }}
        filter(f_rfc5424_noversion);
        parser {
                syslog-parser(flags(syslog-protocol  store-raw-message));
            };
        rewrite(set_rfc5424_noversion);
{{ else if eq (getenv "confgen_parser") "cisco_parser" }}
        parser {cisco-parser()};
        rewrite(set_metadata_vendor_product_cisco_ios);
{{ else if eq (getenv "confgen_parser") "rfc3164" }}
        parser {
            syslog-parser(time-zone({{getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(store-raw-message));
        };
        rewrite(set_rfc3164);
{{ else }}
        if {
            filter(f_rfc5424_strict);
            parser {
                    syslog-parser(flags(syslog-protocol  store-raw-message));
                };
            rewrite(set_rfc5424_strict);
        } elif {
            filter(f_rfc5424_noversion);
            parser {
                    syslog-parser(flags(syslog-protocol  store-raw-message));
                };
            rewrite(set_rfc5424_noversion);
        } elif {
            parser {cisco-parser()};
            rewrite(set_metadata_vendor_product_cisco_ios);
        } else {
            parser {
                syslog-parser(time-zone({{getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(store-raw-message));
            };
            rewrite(set_rfc3164);
        };
{{ end }}
        rewrite(r_set_splunk_default);

   };

};
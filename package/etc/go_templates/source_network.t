# The following is the dedicated source port declaration for {{ (print .port_id) }}
# Two log paths will be created -- one for the dedicated port(s) and one for the default (typically port 514)

source s_dedicated_port_{{ .port_id}} {
    channel {
        source {
{{- if ne (getenv  (print "SC4S_LISTEN_" .port_id "_UDP_PORT" ) "no") "no" }}
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
{{- end}}
{{- if ne (getenv  (print "SC4S_LISTEN_" .port_id "_TCP_PORT") "no") "no" }}
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
{{- end}}
{{- if ne (getenv  (print "SC4S_LISTEN_" .port_id "_TLS_PORT") "no") "no" }}
            network(
                port({{getenv  (print "SC4S_LISTEN_" .port_id "_TLS_PORT") }})
                transport("tls")
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
                tls(allow-compress(yes)
                    key-file("/opt/syslog-ng/tls/server.key")
                    cert-file("/opt/syslog-ng/tls/server.pem")
                    ssl-options({{- getenv "SC4S_SOURCE_TLS_OPTIONS" "no-sslv2, no-sslv3, no-tlsv1" }})
                    cipher-suite("{{- getenv "SC4S_SOURCE_TLS_CIPHER_SUITE" "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH" }}")
                    )
            );
{{- end}}
        };
        #TODO: #60 Remove this function with enhancement
        rewrite(set_rfcnonconformant);
{{ if eq .parser "rfc5424_strict" }}
        filter(f_rfc5424_strict);
        parser {
                syslog-parser(flags(syslog-protocol  store-raw-message));
            };
        rewrite(set_rfc5424_strict);
{{- else if eq .parser "rfc5424_noversion" }}
        filter(f_rfc5424_noversion);
        parser {
                syslog-parser(flags(syslog-protocol  store-raw-message));
            };
        rewrite(set_rfc5424_noversion);
{{- else if eq .parser "cisco_parser" }}
        parser {cisco-parser()};
        rewrite(set_cisco_ios);
{{- else if eq .parser "cisco_meraki_parser" }}
        parser (p_cisco_meraki);
        rewrite(set_rfc5424_epochtime);
{{- else if eq .parser "rfc3164" }}
        parser {
            syslog-parser(time-zone({{getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(store-raw-message));
        };
        rewrite(set_rfc3164);
{{- else if eq .parser "no_parse" }}
        rewrite(set_no_parse);
{{- else }}
        if {filter(f_rfc5424_strict);
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
            rewrite(set_cisco_ios);
        } elif {
            parser (p_cisco_meraki);
            rewrite(set_rfc5424_epochtime);
        } else {
            parser {
                syslog-parser(time-zone({{getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(store-raw-message));
            };
            rewrite(set_rfc3164);
        };
{{- end }}
        rewrite(r_set_splunk_default);

   };

};
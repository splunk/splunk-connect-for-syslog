{{ define "UDP" }}
        syslog (
                transport("udp")
                so-reuseport(1)
                persist-name("{{ .port_id }}{{ .instance }}")
                port({{ getenv (print "SC4S_LISTEN_" .port_id "_UDP_PORT") "514" }})
                ip-protocol(4)
                so-rcvbuf({{getenv "SC4S_SOURCE_UDP_SO_RCVBUFF" "1703936"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
            );   
{{- end}}

{{ define "T1" }}

# The following is the source port declaration for {{ (print .port_id) }}

source s_{{ .port_id }} {
    channel {
        source {
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_UDP_PORT")) (eq .port_id "DEFAULT") }}
{{- $port_id := .port_id }}
{{- range (math.Seq (getenv "SC4S_SOURCE_LISTEN_UDP_SOCKETS" "1"))}}
{{- $context := dict "instance" . "port_id" $port_id }}
{{- template "UDP"  $context }}
{{- end}}
{{- end}}
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_TCP_PORT")) (eq .port_id "DEFAULT") }}
            network (
                transport("tcp")
                port({{ getenv (print "SC4S_LISTEN_" .port_id "_TCP_PORT") "514" }})
                ip-protocol(4)
                max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
            );
{{- end}}
{{- if (conv.ToBool (getenv "SC4S_SOURCE_TLS_ENABLE" "no")) }}
            network(
                transport("tls")
                port({{ getenv (print "SC4S_LISTEN_" .port_id "_TLS_PORT") "6514" }})
                ip-protocol(4)
                max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
                tls(allow-compress(yes)
                    key-file("/opt/syslog-ng/tls/server.key")
                    cert-file("/opt/syslog-ng/tls/server.pem")
                    ssl-options({{- getenv "SC4S_SOURCE_TLS_OPTIONS" "no-sslv2, no-sslv3, no-tlsv1" }})
                    cipher-suite("{{- getenv "SC4S_SOURCE_TLS_CIPHER_SUITE" "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH" }}")
                    )
            );
{{- end}}
        };
{{ if eq .parser "rfc3164" }}
        parser {
            syslog-parser(time-zone({{getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(assume-utf8, guess-timezone));
        };
        rewrite(set_rfc3164);
{{ else if eq .parser "rfc3164_version" }}
#       filter(f_rfc3164_version);
        rewrite(set_rfc3164_no_version_string);
        parser {
            syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(assume-utf8, guess-timezone));
        };
        rewrite(set_rfc3164_version);
{{ else if eq .parser "rfc5424_strict" }}
#       filter(f_rfc5424_strict);
        parser {
                syslog-parser(flags(assume-utf8, syslog-protocol));
            };
        rewrite(set_rfc5424_strict);
{{ else if eq .parser "rfc5424_noversion" }}
#       filter(f_rfc5424_noversion);
        parser {
                syslog-parser(flags(assume-utf8, syslog-protocol));
            };
        rewrite(set_rfc5424_noversion);
{{ else if eq .parser "cisco_parser" }}
        parser (cisco-parser-ex);
        rewrite(set_cisco_syslog);
{{ else if eq .parser "cisco_meraki_parser" }}
        parser (p_cisco_meraki);
        rewrite(set_rfc5424_epochtime);
{{ else if eq .parser "citrix_netscaler" }}
        parser(p_citrix_netscaler_date);
        rewrite(r_citrix_netscaler_message);
{{ else if eq .parser "cisco_ucm" }}
        parser (p_cisco_ucm_date);
        rewrite (r_cisco_ucm_message);
{{ else if eq .parser "no_parse" }}
        rewrite(set_no_parse);
{{ else if eq .parser "tcp_json" }}
        filter { message('^{') and message('}$') };
        parser {
            json-parser(
                prefix('.json.')
            );
        };
        rewrite(set_tcp_json);    
{{ else }}
        if {
            filter(f_citrix_netscaler_message);
            parser(p_citrix_netscaler_date);
            rewrite(r_citrix_netscaler_message);
        } elif {
            filter(f_f5_bigip_message);
            parser(p_f5_bigip_message);
            rewrite(set_rfc3164);
        } elif {
            filter(f_f5_bigip_irule);
            parser(p_f5_bigip_irule);
            rewrite(set_rfc3164);
        } elif {
            filter(f_cef);                        
            rewrite(set_cef_syslog);            
            parser(p_cef);
        } elif {
            #JSON over IP its not syslog but it can work
            filter { message('^{') and message('}$') };
            parser {
                json-parser(
                    prefix('.json.')
                );
            };
            rewrite(set_tcp_json);            
        } elif {
            filter(f_rfc5424_strict);
            parser {
                    syslog-parser(flags(assume-utf8, syslog-protocol));
                };
            rewrite(set_rfc5424_strict);
        } elif {
            parser (p_cisco_meraki);
            rewrite(set_rfc5424_epochtime);
        } elif {
            parser(cisco-parser-ex);
            rewrite(set_cisco_syslog);
        } elif {
            filter(f_cisco_ucm_message);
            parser (p_cisco_ucm_date);
            rewrite (r_cisco_ucm_message);   
        } elif {
            filter(f_rfc3164_version);
            rewrite(set_rfc3164_no_version_string);
            parser {
                    syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(assume-utf8, guess-timezone));
                };
            rewrite(set_rfc3164_version);
        } elif {
            filter(f_rfc5424_noversion);
            parser {
                    syslog-parser(flags(syslog-protocol));
                };
            rewrite(set_rfc5424_noversion);
        } else {
            parser {
                syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(assume-utf8, guess-timezone));
            };
            rewrite(set_rfc3164);
            if {
                filter { message('^{') and message('}$') };
                parser {
                    json-parser(
                        prefix('.json.')
                    );
                };
                rewrite(set_rfc3164_json);  
            } elif {
                filter { match('^{' value('LEGACY_MSGHDR')) and message('}$') };
                parser {
                    json-parser(
                        prefix('.json.')
                        template('${LEGACY_MSGHDR}${MSG}')
                    );
                };
                rewrite {
                    set('${LEGACY_MSGHDR}${MSG}' value('MSG'));
                    unset(value('LEGACY_MSGHDR'));
                };
                rewrite(set_rfc3164_json);              
            };
        };
{{ end }}
        rewrite(r_set_splunk_default);
        parser {
            vendor_product_by_source();
        };

        if {
            filter { match("." value("fields.sc4s_time_zone") ) };
            rewrite {
                fix-time-zone("${fields.sc4s_time_zone}");
                unset(value("fields.sc4s_time_zone"));
            };
        };
    };
};
{{- end -}}
{{- if or (or (or (getenv  (print "SC4S_LISTEN_" .port_id "_TCP_PORT")) (getenv  (print "SC4S_LISTEN_" .port_id "_UDP_PORT"))) (getenv  (print "SC4S_LISTEN_" .port_id "_TLS_PORT"))) (eq .port_id "DEFAULT") -}}
{{- template "T1" (.) -}}
{{- end -}}

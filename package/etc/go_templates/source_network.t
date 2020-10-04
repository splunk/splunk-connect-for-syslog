{{ define "UDP" }}
{{- $port_id := .port_id }}
{{- $port := .port }}
    {{- range (math.Seq (getenv "SC4S_SOURCE_LISTEN_UDP_SOCKETS" "1"))}}
        syslog (
                transport("udp")
                so-reuseport(1)
                persist-name("{{ $port_id }}_{{ $port }}_{{ . }}")
                port({{ $port }})
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
{{- end}}

{{ define "T1" }}

# The following is the source port declaration for {{ (print .port_id) }}

source s_{{ .port_id }} {
    channel {
        source {
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_UDP_PORT")) (eq .port_id "DEFAULT") }}
{{- $port_id := .port_id }}
{{- range split (getenv (print "SC4S_LISTEN_" .port_id "_UDP_PORT") "514") "," }}                
{{- $context := dict "port" . "port_id" $port_id }}
{{- template "UDP"  $context }}
{{- end}}
{{- end}}
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_TCP_PORT")) (eq .port_id "DEFAULT") }}
        {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_TCP_PORT") "514") "," }}                                
            network (
                transport("tcp")                
                port({{ . }})
                ip-protocol(4)
                max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
            );
        {{- end }}
{{- end}}

{{- if (conv.ToBool (getenv "SC4S_SOURCE_TLS_ENABLE" "no")) }}
    {{- if or (getenv (print "SC4S_LISTEN_" .port_id "_TLS_PORT")) (eq .port_id "DEFAULT") }}
        {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_TLS_PORT") "6514") "," }}                
            network(
                transport("tls")
                port({{ . }})
                ip-protocol(4)
                max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
                tls(allow-compress(yes)                
                    key-file("{{- getenv "SC4S_TLS" "/opt/syslog-ng/tls" }}/server.key")
                    cert-file("{{- getenv "SC4S_TLS" "/opt/syslog-ng/tls"}}/server.pem")
                    ssl-options({{- getenv "SC4S_SOURCE_TLS_OPTIONS" "no-sslv2, no-sslv3, no-tlsv1" }})
                    cipher-suite("{{- getenv "SC4S_SOURCE_TLS_CIPHER_SUITE" "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH" }}")
                    peer-verify(no)
                    )
            );
        {{- end }}            
    {{- end }}                 
{{- end }}

{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_6587_PORT")) (eq .port_id "DEFAULT") }}
        {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_6587_PORT") "601") "," }}                
            syslog (
                transport("tcp")
                port({{ . }})
                ip-protocol(4)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, syslog-protocol)
            );    
        {{- end }}            
{{- end }}  
        };

        {{ tmpl.Exec "t/sp_rfc5424.t" }}                                   
        {{ tmpl.Exec "t/sp_rfc3864_versioned.t" }}                                   

        {{ tmpl.Exec "t/sp_cisco_syslog.t" }}    
        {{ tmpl.Exec "t/sp_rfc3864_epoch.t" }}    

        {{ tmpl.Exec "t/sp_citrix_netscaler.t" }}                                   
        {{ tmpl.Exec "t/sp_f5_bigip.t" }}    

        {{ tmpl.Exec "t/sp_rfc3864.t" }}                                   
        
    
        rewrite(r_set_splunk_default);
        {{ if eq (getenv "SC4S_USE_REVERSE_DNS" "no") "yes" }}
        if {
            filter(f_host_is_ip);
            parser(p_add_context_host);
        };        
        if {
            filter(f_host_is_ip);
            parser(p_fix_host_resolver);
        };
        {{ end }}
        parser(vendor_product_by_source);

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

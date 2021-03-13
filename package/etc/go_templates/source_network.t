{{ define "PROTO" -}}
ip-protocol({{- test.Ternary 6 4 (conv.ToBool (getenv "SC4S_IPV6_ENABLE" "no"))}})
{{- end -}}
{{ define "UDP" }}
{{- $port_id := .port_id }}
{{- $port := .port }}
    {{- range (math.Seq (getenv "SC4S_SOURCE_LISTEN_UDP_SOCKETS" "1"))}}
        syslog (
                transport("udp")
                so-reuseport(1)
                persist-name("{{ $port_id }}_{{ $port }}_{{ . }}")
                port({{ $port }})
                {{ template "PROTO" }}
                so-rcvbuf({{getenv "SC4S_SOURCE_UDP_SO_RCVBUFF" "17039360"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
            );   
    {{- end}}
{{- end}}

{{ define "UDP5426" }}
{{- $port_id := .port_id }}
{{- $port := .port }}
    {{- range (math.Seq (getenv "SC4S_SOURCE_LISTEN_UDP_SOCKETS" "1"))}}
        syslog (
                transport("udp")
                so-reuseport(1)
                persist-name("5426{{ $port_id }}_{{ $port }}_{{ . }}")
                port({{ $port }})
                {{ template "PROTO" }}
                so-rcvbuf({{getenv "SC4S_SOURCE_UDP_SO_RCVBUFF" "17039360"}})
                keep-hostname(yes)
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8)
            );   
    {{- end}}
{{- end}}

{{ define "T1" }}

# The following is the source port declaration for {{ (print .port_id) }} if no port is enabled this will generate empty channels that simply
# won't be executed at run time
source s_{{ .port_id }} {
    # Generic Syslog UDP
{{- if or (or (or (getenv  (print "SC4S_LISTEN_" .port_id "_TCP_PORT")) (getenv  (print "SC4S_LISTEN_" .port_id "_UDP_PORT"))) (getenv  (print "SC4S_LISTEN_" .port_id "_TLS_PORT"))) (eq .port_id "DEFAULT") }}    
    channel {
        source {
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_UDP_PORT")) (eq .port_id "DEFAULT") }}
        {{- $port_id := .port_id }}
        {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_UDP_PORT") "514") "," }}                
        {{- $context := dict "port" . "port_id" $port_id }}
        {{- template "UDP"  $context }}
        {{- end}}
{{- end}}
    # Generic Syslog TCP
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_TCP_PORT")) (eq .port_id "DEFAULT") }}
        {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_TCP_PORT") "514") "," }}                                
            network (
                transport("tcp")                
                port({{ . }})
                {{ template "PROTO" }}
                max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                so-rcvbuf({{getenv "SC4S_SOURCE_TCP_SO_RCVBUFF" "17039360"}})
                keep-timestamp(yes)
                use-dns(no)
                use-fqdn(no)
                chain-hostnames(off)
                flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
            );
        {{- end }}
{{- end }}        
{{- if (conv.ToBool (getenv "SC4S_SOURCE_TLS_ENABLE" "no")) }}
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_TLS_PORT")) (eq .port_id "DEFAULT") }}
    {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_TLS_PORT") "6514") "," }}                
        network(
            transport("tls")
            port({{ . }})
            {{ template "PROTO" }}
            max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
            log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
            log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
            so-rcvbuf({{getenv "SC4S_SOURCE_TCP_SO_RCVBUFF" "17039360"}})
            keep-timestamp(yes)
            use-dns(no)
            use-fqdn(no)
            chain-hostnames(off)
            flags(validate-utf8, no-parse {{- if (conv.ToBool (getenv "SC4S_SOURCE_STORE_RAWMSG" "no")) }} store-raw-message {{- end}})
            tls(allow-compress(yes)                
                key-file("{{- getenv "SC4S_TLS" "/etc/syslog-ng/tls" }}/server.key")
                cert-file("{{- getenv "SC4S_TLS" "/etc/syslog-ng/tls"}}/server.pem")
                ssl-options({{- getenv "SC4S_SOURCE_TLS_OPTIONS" "no-sslv2, no-sslv3, no-tlsv1" }})
                cipher-suite("{{- getenv "SC4S_SOURCE_TLS_CIPHER_SUITE" "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH" }}")
                peer-verify(no)
                )
        );
    {{- end }}                    
{{- end }}            
{{- end }}        
        };
        rewrite(r_set_splunk_default);
        
        if {
            parser { app-parser(topic(raw-syslog)); };        
        } else {
            parser {
                syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(assume-utf8, guess-timezone, store-raw-message));
            };
            rewrite(set_rfc3164);  
            
            if {
                # If program is probably not valid cleanup MESSAGE so log paths don't have too
                # This isn't great for performance but is reliable good reason to use 5424
                filter{
                    "${MSGHDR}" ne "${LEGACY_MSGHDR}" or 
                    not program('^[a-zA-Z0-9-_\/\(\)]+$')
                };
                rewrite {
                    set("$(template t_hdr_msg)" value("MSG"));
                    unset(value("LEGACY_MSGHDR"));
                    unset(value("PID"));                
                    unset(value("PROGRAM"));                
                };                    
            };           
            
        };     

        if {
            parser { app-parser(topic(syslog)); };
        } else {
            parser(pattern_db);
        };                

        if {
            parser(p_add_context_host);
        };        
        {{ if eq (getenv "SC4S_USE_REVERSE_DNS" "no") "yes" }}
        if {
            filter(f_host_is_ip);
            parser(p_fix_host_resolver);
        };
        {{ end }}
        rewrite {
                groupunset(values(".raw.*"));
        };        
        
        parser(vendor_product_by_source);
        if {
            parser { app-parser(topic(network-source)); };
        };
        
        if {
            filter { match("." value(".netsource.sc4s_time_zone") ) };
            rewrite {
                fix-time-zone("${.netsource.sc4s_time_zone}");
                unset(value(".netsource.sc4s_time_zone"));
            };
        };
        
    };    
{{- end }}        

    


    #RFC 6587
{{- if or (or (or (getenv  (print "SC4S_LISTEN_" .port_id "_RFC6587_PORT")) (getenv  (print "SC4S_LISTEN_" .port_id "_RFC5426_PORT"))) (getenv  (print "SC4S_LISTEN_" .port_id "_RFC5425_PORT"))) (eq .port_id "DEFAULT") }}    

    channel {
        source {
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_RFC5426_PORT")) (eq .port_id "DEFAULT") }}
        {{- $port_id := .port_id }}
        {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_RFC5426_PORT") "601") "," }}                
        {{- $context := dict "port" . "port_id" $port_id }}
        {{- template "UDP5426"  $context }}
        {{- end}}
{{- end}}

{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_RFC6587_PORT")) (eq .port_id "DEFAULT") }}
            {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_RFC6587_PORT") "601") "," }}                
                syslog (
                    transport("tcp")
                    port({{ . }})
                    {{ template "PROTO" }}
                    max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
                    log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
                    log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
                    so-rcvbuf({{getenv "SC4S_SOURCE_TCP_SO_RCVBUFF" "17039360"}})
                    keep-timestamp(yes)
                    use-dns(no)
                    use-fqdn(no)
                    chain-hostnames(off)
                    flags(validate-utf8, syslog-protocol)
                );    
            {{- end }}            
{{- end }}            
{{- if (conv.ToBool (getenv "SC4S_SOURCE_TLS_ENABLE" "no")) }}
{{- if or (getenv (print "SC4S_LISTEN_" .port_id "_RFC5425_PORT")) (eq .port_id "DEFAULT") }}
    {{- range split (getenv (print "SC4S_LISTEN_" .port_id "_RFC5425_PORT") "5425") "," }}                
        syslog(
            transport("tls")
            port({{ . }})
            {{ template "PROTO" }}
            max-connections({{getenv "SC4S_SOURCE_TCP_MAX_CONNECTIONS" "2000"}})
            log-iw-size({{getenv "SC4S_SOURCE_TCP_IW_SIZE" "20000000"}})
            log-fetch-limit({{getenv "SC4S_SOURCE_TCP_FETCH_LIMIT" "2000"}})
            so-rcvbuf({{getenv "SC4S_SOURCE_TCP_SO_RCVBUFF" "17039360"}})
            keep-timestamp(yes)
            use-dns(no)
            use-fqdn(no)
            chain-hostnames(off)
            flags(validate-utf8, syslog-protocol)
            tls(allow-compress(yes)                
                key-file("{{- getenv "SC4S_TLS" "/etc/syslog-ng/tls" }}/server.key")
                cert-file("{{- getenv "SC4S_TLS" "/etc/syslog-ng/tls"}}/server.pem")
                ssl-options({{- getenv "SC4S_SOURCE_TLS_OPTIONS" "no-sslv2, no-sslv3, no-tlsv1" }})
                cipher-suite("{{- getenv "SC4S_SOURCE_TLS_CIPHER_SUITE" "HIGH:!aNULL:!eNULL:!kECDH:!aDH:!RC4:!3DES:!CAMELLIA:!MD5:!PSK:!SRP:!KRB5:@STRENGTH" }}")
                peer-verify(no)
                )
        );
    {{- end }}                    
{{- end }}   
{{- end }}   

        };
        rewrite(r_set_splunk_default);        
        rewrite {set("rfc5424_strict", value("fields.sc4s_syslog_format") );};
        if {
            parser { app-parser(topic(syslog)); };
        } else {
            parser(pattern_db);
        };        
        
       
        if {
            filter(f_host_is_nil_or_ip);
            parser(p_add_context_host);
        };        
        {{ if eq (getenv "SC4S_USE_REVERSE_DNS" "no") "yes" }}
        if {
            filter(f_host_is_nil_or_ip);
            parser(p_fix_host_resolver);
        };        
        {{ end }}
        parser(vendor_product_by_source);
        if {
            parser { app-parser(topic(network-source)); };
        };
        
    };


{{- end }}
}; 
{{- end }}


{{- template "T1" (.) -}}

        if {
            filter(f_is_not_format);
            filter(f_f5_bigip_message);
            rewrite{
                set('$2' 
                        value('fields.host_blade')
                        condition(match("." value('2')))
                );
            };
            parser(p_f5_bigip_message);
            rewrite(set_rfc3164);
        };
        if {
            filter(f_is_not_format);
            filter(f_f5_bigip_irule);

            parser {
                syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(no-hostname, assume-utf8, guess-timezone));
            };
            rewrite(set_rfc3164);
        };
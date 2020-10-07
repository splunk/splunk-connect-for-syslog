        if {
                filter(f_is_not_format);
                filter(f_rfc5424_strict);
                if {
                    parser { app-parser(topic(syslog)); };
                };
                parser {
                        syslog-parser(flags(assume-utf8, syslog-protocol));
                    };
                rewrite(set_rfc5424_strict);
        };
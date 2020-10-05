        if {
            filter(f_is_not_format);
            parser(cisco-parser-ex);
            rewrite(set_cisco_syslog);
        };
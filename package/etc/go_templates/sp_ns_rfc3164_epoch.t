        if {
            filter(f_is_not_format);
            filter(f_rfc3164_epoch);
            parser(p_rfc3164_epoch);
            rewrite(set_rfc3164_epoch);
        };
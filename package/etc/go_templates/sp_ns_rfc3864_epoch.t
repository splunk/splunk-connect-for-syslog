        if {
            filter(f_is_not_format);
            filter(f_rfc3864_epoch);
            parser(p_rfc3864_epoch);
            rewrite(set_rfc3164_epoch);
        };
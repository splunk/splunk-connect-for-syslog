        #If this event isn't strict RFC5424 we need to remove the version indicator as it will trip up the parsers
        if {
            filter(f_is_not_format);
            filter(f_rfc3164_version);
            rewrite(set_rfc3164_no_version_string);    
        };
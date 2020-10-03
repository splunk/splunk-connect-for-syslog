if {
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
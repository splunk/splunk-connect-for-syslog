if {
    filter(f_is_not_format);
    filter(f_f5_bigip_irule);

    parser {
        syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(no-hostname, assume-utf8, guess-timezone));
    };
    rewrite(set_rfc3164);
};
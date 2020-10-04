if {
    filter(f_is_not_format);
    filter(f_rfc3164_version);
    rewrite(set_rfc3164_no_version_string);
    parser {
        syslog-parser(time-zone({{- getenv "SC4S_DEFAULT_TIMEZONE" "GMT"}}) flags(assume-utf8, guess-timezone));
    };
    rewrite(set_rfc3164_version);
};
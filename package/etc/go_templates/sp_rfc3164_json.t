        if {
            filter(f_is_rfc3164);
            if {
                filter { message('^{') and message('}$') };
                parser {
                    json-parser(
                        prefix('.json.')
                    );
                };
                rewrite(set_rfc3164_json);  
            } elif {
                filter { match('^{' value('LEGACY_MSGHDR')) and message('}$') };
                parser {
                    json-parser(
                        prefix('.json.')
                        template('${LEGACY_MSGHDR}${MSG}')
                    );
                };
                rewrite {
                    set('${LEGACY_MSGHDR}${MSG}' value('MSG'));
                    unset(value('LEGACY_MSGHDR'));
                };
                rewrite(set_rfc3164_json);              
            };    
        };
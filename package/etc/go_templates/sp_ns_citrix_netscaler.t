        if {          
            filter(f_is_not_format);
            filter(f_citrix_netscaler_message);
            parser { 
    {{- if (conv.ToBool (getenv "SC4S_SOURCE_CITRIX_NETSCALER_USEALT_DATE_FORMAT" "no")) }}        
                date-parser-nofilter(format('%m/%d/%Y:%H:%M:%S')
    {{- else }}        
                date-parser-nofilter(format('%d/%m/%Y:%H:%M:%S')
    {{- end }}
                template("$CITRIXDATE"));
            };
            rewrite(r_citrix_netscaler_message);
        } elif {
            filter(f_citrix_netscaler_sdx_message);
            parser { date-parser-nofilter(format('%b %d %H:%M:%S')
                template("$CITRIXDATE"));
            };
            rewrite(r_citrix_netscaler_sdx_message);        
        } elif {
            filter(f_citrix_netscaler_sdx_AAAmessage);
            parser { 
                date-parser-nofilter(format('%b %d %H:%M:%S')
                template("$CITRIXDATE"));
            };
            rewrite(r_citrix_netscaler_sdx_AAAmessage);             
        } elif {
            filter(f_citrix_netscaler_vpx_message);
            parser {
                date-parser-nofilter(format('%b %d %H:%M:%S')
                template("$CITRIXDATE"));
            };
            rewrite(r_citrix_netscaler_vpx_message);
        } else {};
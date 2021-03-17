{{ define "L1" }}

log {
    junction {
        {{- if has . "port_id" }}
        channel {
        # Listen on the specified dedicated port(s) for {{ .port_id }} traffic
            source (s_{{ .port_id }});
            {{- if has . "port_filter" }}
            filter({{ .port_filter }});
            {{- end}}
            flags (final);
	    };
        {{- end}}
        {{- if has . "group_port_id" }}
        channel {
        
            source (s_{{ .group_port_id }});
            {{- if has . "soup_filter" }}
            filter({{ .soup_filter }});
            {{- end}}
            flags (final);
	    };
        {{- end}}
        channel {
        # Listen on the default port (typically 514) for {{ .port_id }} traffic
            source (s_DEFAULT);
            filter({{ .soup_filter }});
            flags(final);
        };
    };


    junction {
        {{- if or (conv.ToBool (getenv "SC4S_DEST_SPLUNK_HEC_GLOBAL" "yes")) (conv.ToBool (getenv (print "SC4S_DEST_" .port_id "_HEC" "no"))) }}
        channel {
            destination(d_hec);
	    };        
        {{ end}}
        
        {{- if or (conv.ToBool (getenv "SC4S_ARCHIVE_GLOBAL" "yes")) (conv.ToBool (getenv (print "SC4S_ARCHIVE_" .port_id "_HEC" "no"))) }}
        channel {
            destination(d_archive);
	    };        
        {{ end}}
        
        {{- if getenv "SC4S_DEST_GLOBAL_ALTERNATES" }}
        channel {
            {{ getenv "SC4S_DEST_GLOBAL_ALTERNATES" | regexp.ReplaceLiteral "^" "destination(" | regexp.ReplaceLiteral "[, ]+" ");\n    destination(" }});
	    };        
        {{ end}}
        
        {{- if (conv.ToBool (getenv (print "SC4S_DEST_" .port_id "_ALTERNATES" "yes"))) }}
        channel {
            {{ getenv (print "SC4S_DEST_" .port_id "_ALTERNATES") | regexp.ReplaceLiteral "^" "destination(" | regexp.ReplaceLiteral "[, ]+" ");\n    destination(" }});
	    };        
        {{ end}}
        
        {{- if and (getenv (print "SC4S_DEST_" .port_id "_ALT_FILTER")) (getenv (print "SC4S_DEST_" .port_id "_FILTERED_ALTERNATES")) }}
        channel {
            filter({{ getenv (print "SC4S_DEST_" .port_id "_ALT_FILTER") }});
            {{ getenv (print "SC4S_DEST_" .port_id "_FILTERED_ALTERNATES") | regexp.ReplaceLiteral "^" "destination(" | regexp.ReplaceLiteral "[, ]+" ");\n        destination(" }});
	    };        
        {{ end}}
        
    };  
  

    flags(flow-control,final);
};



{{- end}}
{{- template "L1" (.) -}}
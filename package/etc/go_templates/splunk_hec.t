{{ define "SPLUNK_HEC" }}
destination d_hec{{ .var_id }} {
    {{- $url := (getenv (print "SPLUNK_HEC" .var_id "_URL") | strings.Trim " " ) }}
    http(
         url("{{- $url }}")
         method("POST")
         log-fifo-size({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_LOG_FIFO_SIZE") "180000000"}})
         workers({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_WORKERS") "10"}})
         batch-lines({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_BATCH_LINES") "1000"}})
         batch-bytes({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_BATCH_BYTES") "4096kb"}})
         batch-timeout({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_BATCH_TIMEOUT") "3000"}})
         timeout({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_TIMEOUT") "30"}})
         user_agent("sc4s/1.0 (events)")
         user("sc4s")
         headers("{{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_HEADERS") "Connection: close"}}")
         password("{{- getenv (print "SPLUNK_HEC" .var_id "_TOKEN") | strings.Trim " " }}")
         persist-name("splunk_hec{{ .var_id }}")
         response-action(400 => drop, 404 => retry)

         {{- if eq (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_ENABLE") "yes") "yes"}}

         disk-buffer(

            {{- if eq (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_RELIABLE") "no") "yes"}}
            mem-buf-size({{conv.ToInt64 (math.Round ( math.Div (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_MEMBUFSIZE") "10241024") (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_WORKERS") "10")))}})
            reliable(yes)
            {{- else}}
            mem-buf-length({{conv.ToInt64 (math.Round ( math.Div (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_MEMBUFLENGTH") "15000") (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_WORKERS") "10")))}})
            reliable(no)
            {{- end}}
            {{- if ne (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_DIR")) ""}}
            dir("{{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_DIR")}}")
            {{- end}}
            disk-buf-size({{conv.ToInt64 (math.Round ( math.Div (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_DISKBUFF_DISKBUFSIZE") "53687091200") (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_WORKERS") "10")))}})
             )
         {{- end}}
         tls(peer-verify({{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_TLS_VERIFY") "yes"}})
         {{- if ne (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_CIPHER_SUITE")) ""}}
         cipher-suite("{{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_CIPHER_SUITE")}}")
         {{- end}}
         {{- if ne (getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_SSL_VERSION")) ""}}
         ssl-version("{{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_SSL_VERSION")}}")
         {{- end}}
         ca-file("{{- getenv (print "SC4S_DEST_SPLUNK_HEC" .var_id "_TLS_CA_FILE") "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"}}"))
         body('$(format-json
                 time=$S_UNIXTIME
                 host=${.splunk.host}
                 source=${.splunk.source}
                 sourcetype=${.splunk.sourcetype}
                 index=${.splunk.index}
                 event="$MSG"
                 {{- if ne (getenv (print "SC4S_DEST_SPLUNK_INDEXED_FIELDS")) "none" }}
                 fields.*
                 {{- end }}
                 )')
        );
};

{{- end -}}

{{- template "SPLUNK_HEC" (.) -}}

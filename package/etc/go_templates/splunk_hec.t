{{ define "SPLUNK_HEC" }}
destination d_hec{{ .dest_id }} {
    http(
         url("{{- getenv "SPLUNK_HEC_URL" | strings.ReplaceAll "/services/collector" "" | strings.ReplaceAll "/event" "" | regexp.ReplaceLiteral "[, ]+" "/services/collector/event " }}/services/collector/event")
         method("POST")
         log-fifo-size({{- getenv (print "SC4S_DEST_SPLUNK_HEC_LOG_FIFO_SIZE") "180000000"}})
         workers({{- getenv (print "SC4S_DEST_SPLUNK_HEC_WORKERS") "10"}})
         batch-lines({{- getenv (print "SC4S_DEST_SPLUNK_HEC_BATCH_LINES") "1000"}})
         batch-bytes({{- getenv (print "SC4S_DEST_SPLUNK_HEC_BATCH_BYTES") "4096kb"}})
         batch-timeout({{- getenv (print "SC4S_DEST_SPLUNK_HEC_BATCH_TIMEOUT") "3000"}})
         timeout({{- getenv (print "SC4S_DEST_SPLUNK_HEC_TIMEOUT") "30"}})
         user_agent("sc4s/1.0 (events)")
         user("sc4s")
         headers("{{- getenv (print "SC4S_DEST_SPLUNK_DEST_SPLUNK_HEC_HEADERS") "Connection: close"}}")
         password("{{- getenv (print "SPLUNK_HEC_TOKEN")}}")
         persist-name("splunk_hec")
         response-action(400 => drop, 404 => retry)

         {{- if eq (getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_ENABLE") "yes") "yes"}}

         disk-buffer(

            {{- if eq (getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_RELIABLE") "no") "yes"}}
            mem-buf-size({{conv.ToInt64 (math.Round ( math.Div (getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_MEMBUFSIZE") "10241024") (getenv (print "SC4S_DEST_SPLUNK_HEC_WORKERS") "10")))}})
            reliable(yes)
            {{- else}}
            mem-buf-length({{conv.ToInt64 (math.Round ( math.Div (getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_MEMBUFLENGTH") "15000") (getenv (print "SC4S_DEST_SPLUNK_HEC_WORKERS") "10")))}})
            reliable(no)
            {{- end}}
            {{- if ne (getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_DIR")) ""}}
            dir("{{- getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_DIR")}}")
            {{- end}}
            disk-buf-size({{conv.ToInt64 (math.Round ( math.Div (getenv (print "SC4S_DEST_SPLUNK_HEC_DISKBUFF_DISKBUFSIZE") "53687091200") (getenv (print "SC4S_DEST_SPLUNK_HEC_WORKERS") "10")))}})
             )
         {{- end}}
         tls(peer-verify({{- getenv (print "SC4S_DEST_SPLUNK_HEC_TLS_VERIFY") "yes"}})
         {{- if ne (getenv (print "SC4S_DEST_SPLUNK_HEC_CIPHER_SUITE")) ""}}
         cipher-suite("{{- getenv (print "SC4S_DEST_SPLUNK_HEC_CIPHER_SUITE")}}")
         {{- end}}
         {{- if ne (getenv (print "SC4S_DEST_SPLUNK_HEC_SSL_VERSION")) ""}}
         ssl-version("{{- getenv (print "SC4S_DEST_SPLUNK_HEC_SSL_VERSION")}}")
         {{- end}}
         ca-file("{{- getenv (print "SC4S_DEST_SPLUNK_HEC_TLS_CA_FILE") "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"}}"))
         body('$(format-json
                 time=$S_UNIXTIME
                 host=${HOST}
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

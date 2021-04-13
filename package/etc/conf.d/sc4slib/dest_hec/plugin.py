#! /usr/bin/env python3
import os
import shutil
from jinja2 import Template

template = """
destination d_hec{{ dest_mode }}{{ altname }}{
    http(
        url("{{ url }}")
        user('sc4s')
        password("{{ token }}")
        method("POST")
        log-fifo-size({{ log_fifo_size }})
        workers({{ workers }})
        batch-lines({{ batch_lines }})
        batch-bytes({{ batch_bytes }})
        batch-timeout({{ batch_timeout }})
        timeout({{ timeout }})
        user_agent("sc4s/1.0 (events)")
        #headers("{{ headers }}")
        persist-name("splunk_hec{{ dest_mode }}{{ group }}")
        response-action(400 => drop, 404 => retry)

    {%- if diskbuff_enable %}   
        disk-buffer(
        {%- if diskbuff_enable %}   
            mem-buf-size({{ mem_buf_size }})            
            reliable(yes)
        {%- else %}
            mem-buf-length({{ mem_buf_length }})
            reliable(no)            
        {%- endif %}
            disk-buf-size({{ disk_buf_size }})            
        )
        tls(
            peer-verify({{ peer_verify }})
        {%- if cipher_suite %}   
            cipher-suite("{{ cipher_suite }}")
        {%- endif %}
        {%- if ssl_version %}   
            ssl-version("{{ ssl_version }}")
        {%- endif %}
            ca-file("{{ tls_ca_file }}")
        )
    {%- endif %}
        body('{{ msg_template }}')
    );
};

"""

tm = Template(template)
mode = os.getenv("confgen_mode")

msg_template = "$(template t_splunk_hec_event_legacy)"
dest_mode = ""
if mode == "fmt":
    msg_template = "$(template ${.splunk.sc4s_hec_template} $(template t_splunk_hec))"
    dest_mode = "_fmt"

# SPLUNK_HEC_ALT_DESTS
dests = f'DEFAULT,{ os.getenv("SPLUNK_HEC_ALT_DESTS","") }'.rstrip(",").split(",")
for group in dests:
    altname = ""
    if group != "DEFAULT":
        altname = f"_{ group }"

    # print (mode)
    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_HEADERS", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_enable = True
    else:
        diskbuff_enable = False

    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_HEADERS", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_reliable = True
    else:
        diskbuff_reliable = False

    # Used to calc disk space for buffer
    disk_space, used, free = shutil.disk_usage(os.getenv(f"SC4S_VAR", "/"))
    disk_space = disk_space - 5 * 1024 * 1024 * 1024

    workers = os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_WORKERS", 10)
    msg = tm.render(
        group=group,
        altname=altname,
        msg_template=msg_template,
        dest_mode=dest_mode,
        url=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_URL"),
        token=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_TOKEN"),
        log_fifo_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_LOG_FIFO_SIZE", 180000000
        ),
        workers=workers,
        batch_lines=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_BATCH_LINES", 5000),
        batch_bytes=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_BATCH_BYTES", "4096kb"),
        batch_timeout=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_BATCH_TIMEOUT", 300),
        timeout=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_TIMEOUT", 30),
        headers=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_HEADERS", "Connection: close"
        ),
        diskbuff_enable=diskbuff_enable,
        diskbuff_reliable=diskbuff_reliable,
        mem_buf_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_DISKBUFF_MEMBUFSIZE",
            int(163840000 / workers),
        ),
        mem_buf_length=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_DISKBUFF_MEMBUFLENGTH",
            int(60000 / workers),
        ),
        disk_buf_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_DISKBUFF_DISKBUFSIZE",
            int(disk_space / workers),
        ),
        peer_verify=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_TLS_VERIFY", "yes"),
        cipher_suite=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_CIPHER_SUITE"),
        ssl_version=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_SSL_VERSION"),
        tls_ca_file=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_TLS_CA_FILE",
            "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
        ),
    )

    print(msg)

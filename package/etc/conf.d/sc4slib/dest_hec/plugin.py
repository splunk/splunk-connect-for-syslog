#! /usr/bin/env python3
import os
import shutil
import jinja2

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

mode = os.getenv("confgen_mode")

msg_template = "$(template t_splunk_hec_event_legacy)"
dest_mode = ""
if mode == "fmt":
    msg_template = "$(template ${.splunk.sc4s_hec_template} $(template t_splunk_hec))"
    dest_mode = "_fmt"

dests = f'DEFAULT,{ os.getenv("SPLUNK_HEC_ALT_DESTS","") }'.rstrip(",").split(",")
for group in dests:
    altname = ""
    if group != "DEFAULT":
        altname = f"_{ group }"

    # print (mode)
    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_DISKBUFF_ENABLE", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_enable = True
    else:
        diskbuff_enable = False

    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_DISKBUFF_RELIABLE", "no").lower() in [
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
    disk_space = disk_space - 5000000000

    if disk_space < 0:
        disk_space = 5000000000

    workers = os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_WORKERS", 10)
    headers = []
    user_headers = os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_HEADERS", ""
        )
    if user_headers!="":
        headers += user_headers.split(",")

    token=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_TOKEN")     
    headers.append(f"Authorization: Splunk {token}")

    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_CONNECTION_CLOSE", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        headers.append(f"Connection: close")
    else:
        headers.append(f"Connection: keep-alive")


    msg = tm.render(
        group=group,
        altname=altname,
        msg_template=msg_template,
        dest_mode=dest_mode,
        url=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_URL"),
        log_fifo_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{ group }_LOG_FIFO_SIZE", 180000000
        ),
        workers=workers,
        batch_lines=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_BATCH_LINES", 5000),
        batch_bytes=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_BATCH_BYTES", "4096kb"),
        batch_timeout=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_BATCH_TIMEOUT", 300),
        timeout=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{ group }_TIMEOUT", 30),
        headers='"{0}"'.format('", "'.join(headers)),
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
        
    )

    print(msg)

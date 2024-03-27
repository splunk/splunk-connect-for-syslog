#! /usr/bin/env python3
import os
import shutil
import jinja2
import re

def hec_endpoint_collector(hec_path, url_hec):
    """the function is used to validate if the alternate destination url is correct"""
    if hec_path in url_hec:
        endpoint = url_hec
    else:
        endpoint = f"{url_hec}{hec_path}"
    return endpoint

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(
    loader=templateLoader,
    autoescape=jinja2.select_autoescape(default_for_string=False),
)
tm = templateEnv.get_template("plugin.jinja")

msg_template = "$(template ${.splunk.sc4s_hec_template} $(template t_splunk_hec))"
dest_mode = "_fmt"
dests = []

regex = r"^SC4S_DEST_SPLUNK_HEC_(.*)_URL$"
for vn, vv in os.environ.items():
    m = re.search(regex, vn)
    r = m.group(1) if m else ""
    if r != "":
        dests.append(r)

for group in dests:
    url = os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_URL")
    altname = ""
    if group != "DEFAULT":
        altname = f"_{group}".lower()
        hec_endpoint_path = "/services/collector/event"
        url = hec_endpoint_collector(hec_endpoint_path, url)

    # print (mode)
    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_DISKBUFF_ENABLE", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_enable = True
    else:
        diskbuff_enable = False

    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_DISKBUFF_RELIABLE", "no").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_reliable = True
    else:
        diskbuff_reliable = False

# Disk buffer directory for BYOE setup , don't use it for container solutions
    buff_dir = os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_DISKBUFF_DIR", "")
    if buff_dir != "":
        buff_dir_enable = True
    else:
        buff_dir_enable = False

    # Used to calc disk space for buffer
    disk_space, used, free = shutil.disk_usage(os.getenv("SC4S_VAR", "/"))
    disk_space = disk_space - 5000000000

    if disk_space < 0:
        disk_space = 5000000000

    workers = int(os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_WORKERS", 10))
    headers = []
    user_headers = os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_HEADERS", "")
    if user_headers != "":
        headers += user_headers.split(",")
    token = os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_TOKEN")
    headers.append(f"Authorization: Splunk {token}")
    headers.append("__splunk_app_name: sc4syslog")
    sc4s_version = os.getenv('SC4S_VERSION', "0.0.0")
    headers.append(f"__splunk_app_version: {sc4s_version}")

    user_agent = f"sc4s/{sc4s_version}"

    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_CONNECTION_CLOSE", "no").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        headers.append("Connection: close")
    else:
        headers.append("Connection: keep-alive")

    if os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_HTTP_COMPRESSION", "no").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        http_compression = True
    else:
        http_compression = False

    msg = tm.render(
        group=group,
        altname=altname,
        msg_template=msg_template,
        dest_mode=dest_mode,
        url=url,
        log_fifo_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{group}_LOG_FIFO_SIZE", 180000000
        ),
        workers=workers,
        batch_lines=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_BATCH_LINES", 5000),
        batch_bytes=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_BATCH_BYTES", "4096kb"),
        batch_timeout=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_BATCH_TIMEOUT", 300),
        timeout=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_TIMEOUT", 30),
        user_agent=user_agent,
        buff_dir=buff_dir,
        buff_dir_enable=buff_dir_enable,
        headers='"{0}"'.format('", "'.join(headers)),
        diskbuff_enable=diskbuff_enable,
        diskbuff_reliable=diskbuff_reliable,
        mem_buf_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{group}_DISKBUFF_MEMBUFSIZE",
            int(163840000 / workers),
        ),
        mem_buf_length=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{group}_DISKBUFF_MEMBUFLENGTH",
            int(60000 / workers),
        ),
        disk_buf_size=os.getenv(
            f"SC4S_DEST_SPLUNK_HEC_{group}_DISKBUFF_DISKBUFSIZE",
            int(disk_space / workers),
        ),
        tls_mount=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_TLS_MOUNT"),
        peer_verify=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_TLS_VERIFY", "yes"),
        cipher_suite=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_CIPHER_SUITE"),
        ssl_version=os.getenv(f"SC4S_DEST_SPLUNK_HEC_{group}_SSL_VERSION"),
        http_compression=http_compression
    )

    print(msg)

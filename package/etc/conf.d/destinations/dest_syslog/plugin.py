#! /usr/bin/env python3
import os
import shutil
import jinja2
import re

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(
    loader=templateLoader,
    autoescape=jinja2.select_autoescape(default_for_string=False),
)
tm = templateEnv.get_template("plugin.jinja")

msg_template = "$(template t_syslog)"
dests = []

regex = r"^SC4S_DEST_SYSLOG_(.*)_HOST$"
for vn, vv in os.environ.items():
    m = re.search(regex, vn)
    r = m.group(1) if m else ""
    if r != "":
        dests.append(r)

for group in dests:
    altname = f"_{ group }".lower()

    # print (mode)
    if os.getenv(f"SC4S_DEST_SYSLOG_{ group }_DISKBUFF_ENABLE", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_enable = True
    else:
        diskbuff_enable = False

    if os.getenv(f"SC4S_DEST_SYSLOG_{ group }_DISKBUFF_RELIABLE", "no").lower() in [
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
    disk_space, used, free = shutil.disk_usage(os.getenv("SC4S_VAR", "/"))
    disk_space = disk_space - 5000000000

    if disk_space < 0:
        disk_space = 5000000000
    if os.getenv(f"SC4S_DEST_SYSLOG_{ group }_IETF", "yes") in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        port = os.getenv(f"SC4S_DEST_SYSLOG_{ group }_PORT", 601)
        framed = True
    else:
        port = os.getenv(f"SC4S_DEST_SYSLOG_{ group }_PORT", 514)
        framed = False

    transport = os.getenv(f"SC4S_DEST_SYSLOG_{ group }_TRANSPORT", "tcp")

    #### if TLS is used as a transport type
    tls = True if transport in ["tls", "TLS"] else False

    msg = tm.render(
        tls=tls,
        group=group,
        framed=framed,
        altname=altname,
        port=port,
        transport=transport,
        host=os.getenv(f"SC4S_DEST_SYSLOG_{ group }_HOST"),
        log_fifo_size=os.getenv(f"SC4S_DEST_SYSLOG_{ group }_LOG_FIFO_SIZE", 180000000),
        diskbuff_enable=diskbuff_enable,
        diskbuff_reliable=diskbuff_reliable,
        mem_buf_size=os.getenv(
            f"SC4S_DEST_SYSLOG_{ group }_DISKBUFF_MEMBUFSIZE",
            int(163840000),
        ),
        mem_buf_length=os.getenv(
            f"SC4S_DEST_SYSLOG_{ group }_DISKBUFF_MEMBUFLENGTH",
            int(60000),
        ),
        disk_buf_size=os.getenv(
            f"SC4S_DEST_SYSLOG_{ group }_DISKBUFF_DISKBUFSIZE",
            int(disk_space),
        ),
        peer_verify=os.getenv(f"SC4S_DEST_SYSLOG_{ group }_TLS_VERIFY", "yes"),
        cipher_suite=os.getenv(f"SC4S_DEST_SYSLOG_{ group }_CIPHER_SUITE"),
        ssl_version=os.getenv(f"SC4S_DEST_SYSLOG_{ group }_SSL_VERSION"),
    )

    print(msg)

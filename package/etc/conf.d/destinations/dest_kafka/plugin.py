#! /usr/bin/env python3
import os
import shutil
import jinja2
import re

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

msg_template = "$(template t_kafka)"
dests = []

regex = r"^SC4S_DEST_KAFKA_(.*)_BOOTSTRAP_SERVERS$"
for vn, vv in os.environ.items():
    m = re.search(regex, vn)
    r = m.group(1) if m else ""
    if r != "":
        dests.append(r)

for group in dests:
    altname = f"_{ group }".lower()

    # print (mode)
    if os.getenv(f"SC4S_DEST_KAFKA_{ group }_DISKBUFF_ENABLE", "yes").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        diskbuff_enable = True
    else:
        diskbuff_enable = False

    # Disk buffer directory for BYOE setup , don't use it for container solutions
    buff_dir = os.getenv(f"SC4S_DEST_SPLUNK_KAFKA_{group}_DISKBUFF_DIR", "")
    if buff_dir != "":
        buff_dir_enable = True
    else:
        buff_dir_enable = False

    if os.getenv(f"SC4S_DEST_KAFKA_{ group }_DISKBUFF_RELIABLE", "no").lower() in [
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

    msg = tm.render(
        group=group,
        altname=altname,
        bootstrap_servers=os.getenv(f"SC4S_DEST_KAFKA_{ group }_BOOTSTRAP_SERVERS"),
        topic=os.getenv(f"SC4S_DEST_KAFKA_{ group }_TOPIC","syslog"),
        
        buff_dir=buff_dir,
        buff_dir_enable=buff_dir_enable,
        diskbuff_enable=diskbuff_enable,
        diskbuff_reliable=diskbuff_reliable,
        mem_buf_size=os.getenv(
            f"SC4S_DEST_KAFKA_{ group }_DISKBUFF_MEMBUFSIZE",
            int(163840000),
        ),
        mem_buf_length=os.getenv(
            f"SC4S_DEST_KAFKA_{ group }_DISKBUFF_MEMBUFLENGTH",
            int(60000),
        ),
        disk_buf_size=os.getenv(
            f"SC4S_DEST_KAFKA_{ group }_DISKBUFF_DISKBUFSIZE",
            int(disk_space),
        )
    )
    print(msg)
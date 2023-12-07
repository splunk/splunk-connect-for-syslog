#! /usr/bin/env python3
import os
import jinja2
import re

plugin_path = os.path.dirname(os.path.abspath(__file__))
templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(
    loader=templateLoader,
    autoescape=jinja2.select_autoescape(default_for_string=False),
)
tm = templateEnv.get_template("plugin.jinja")

def normalize_env_variable_input(env_variable: str):
    if os.getenv(env_variable, "no").lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:
        normalized_value = True
    else:
        normalized_value = False
    return normalized_value

                              
regex_splunkhec = r"^SC4S_DEST_SPLUNK_HEC_(.*)_URL$"
regex_syslog = r"^SC4S_DEST_(SYSLOG|BSD)_(.*)_HOST$"
global_dests = {}
for vn, vv in os.environ.items():
    m = re.search(regex_splunkhec, vn)
    r = m.group(1) if m else ""
    # if r != "" and vv == "" and r not in ('DEFAULT','INTERNAL') and vv in ('GLOBAL', 'SELECT'):
    if r != "":
        modev = os.environ.get(f"SC4S_DEST_SPLUNK_HEC_{r}_MODE", "GLOBAL")
        if (
            r == "DEFAULT"
            and not os.environ.get("SC4S_DEST_SPLUNK_HEC_GLOBAL", "") == ""
        ):
            if os.environ.get("SC4S_DEST_SPLUNK_HEC_GLOBAL", "yes").lower() in [
                "true",
                "1",
                "t",
                "y",
                "yes",
            ]:
                modev = "GLOBAL"
            else:
                modev = "SELECT"
        elif modev in ("GLOBAL", "SELECT"):
            suffix = ""
            if r != "DEFAULT":
                suffix = f"_{r}"

        global_dests[r] = {
            "destination": f"d_hec_fmt{suffix.lower()}",
            "dtype": "hec_fmt",
            "mode": modev,
            "filter": "",
        }

for vn, vv in os.environ.items():
    m = re.search(regex_syslog, vn)
    t = m.group(1) if m else ""
    r = m.group(2) if m else ""
    # if r != "" and vv == "" and r not in ('DEFAULT','INTERNAL') and vv in ('GLOBAL', 'SELECT'):
    if r != "":
        modev = os.environ.get(f"SC4S_DEST_{t}_{r}_MODE", "GLOBAL")
        filter = os.environ.get(f"SC4S_DEST_{t}_{r}_FILTER", "")
        if filter == "":
            if t == "BSD":
                filter = '"${MSG}" ne ""'
        if modev.upper() in ("GLOBAL", "SELECT"):
            global_dests[r] = {
                "destination": f"d_{t.lower()}_{r.lower()}",
                "dtype": t.lower(),
                "mode": modev,
                "filter": filter,
            }


for d, m in global_dests.items():
    msg = tm.render(
        id=d,
        destination=m["destination"],
        mode=m["mode"],
        filter=m["filter"],
        dtype=m["dtype"],
        enable_parallelize=normalize_env_variable_input(f"SC4S_ENABLE_PARALLELIZE"),
        parallelize_no_partitions=int(os.getenv(f"SC4S_PARALLELIZE_NO_PARTITION", 4)),
    )
    print(msg)

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


regexfa = r"SC4S_DEST_(.*)(?<!_FILTERED)_ALTERNATES"
for vn, vv in os.environ.items():
    m = re.search(regexfa, vn)

    r = m.group(1) if m else ""
    if r != "" and vv != "" and r != "GLOBAL":
        dests = vv.split(",")
        for d in dests:
            msg = tm.render(destination=d, source=r)
            print(msg)

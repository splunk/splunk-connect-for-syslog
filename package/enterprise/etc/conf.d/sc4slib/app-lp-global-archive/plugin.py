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

keys = []
regex = r"^SC4S_DEST_(.*)_ARCHIVE$"
for vn, vv in os.environ.items():
    m = re.search(regex, vn)
    r = m.group(1) if m else ""
    if r != "" and vv.lower() in [
        "true",
        "1",
        "t",
        "y",
        "yes",
    ]:

        msg = tm.render(
            key=r,
        )

        print(msg)

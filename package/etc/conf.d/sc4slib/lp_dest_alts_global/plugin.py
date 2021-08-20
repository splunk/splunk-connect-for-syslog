#! /usr/bin/env python3
import os
import jinja2

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

if os.getenv("SC4S_DEST_GLOBAL_ALTERNATES"):
    for d in os.getenv("SC4S_DEST_GLOBAL_ALTERNATES").split(","):
        msg = tm.render(destination=d)
        print(msg)

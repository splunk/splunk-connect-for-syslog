#! /usr/bin/env python3

import os
import shutil
import jinja2

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(
    loader=templateLoader,
    autoescape=jinja2.select_autoescape(default_for_string=False),
)
tm = templateEnv.get_template("plugin.jinja")

msg = tm.render(
    stats_freq=os.getenv("SC4S_GLOBAL_OPTIONS_STATS_FREQ", 30),
    stats_level=os.getenv("SC4S_GLOBAL_OPTIONS_STATS_LEVEL", 1),
    log_fifo=os.getenv("SC4S_GLOBAL_OPTIONS_LOG_FIFO", 10000),
)

print(msg)

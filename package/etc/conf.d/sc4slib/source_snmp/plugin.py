#! /usr/bin/env python3
import os
import jinja2


plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

if os.getenv("SC4S_SNMP_TRAP_COLLECT") == "yes":
    msg = tm.render()
    print(msg)

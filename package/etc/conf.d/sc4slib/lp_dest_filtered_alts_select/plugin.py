#! /usr/bin/env python3
import os
import jinja2
import pprint

pp = pprint.PrettyPrinter(indent=4)

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

routes = {}
filters = {}
for var in os.environ:
    if var.startswith("SC4S_DEST_") and var.endswith("_FILTERED_ALTERNATES"):
        dest_key = var.replace("SC4S_DEST_", "").replace("_FILTERED_ALTERNATES", "")
        dest_key_dests = os.environ[var].split(",")

        # create a list of all the dests
        for dd in dest_key_dests:
            if not dd in routes.keys():
                routes[dd] = {}

            if not dest_key in routes[dd].keys():
                routes[dd][dest_key] = os.getenv(
                    f"SC4S_DEST_{ dest_key }_ALT_FILTER", "f_is_nevermatch"
                )

for d in routes.keys():
    filter_list = []
    for df in routes[d]:
        filter_list.append([df, routes[d][df]])

    msg = tm.render(destination=d, filters=filter_list, fcount=len(filter_list))
    print(msg)

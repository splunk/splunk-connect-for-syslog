#! /usr/bin/env python3
import os
import jinja2
import pprint

pp = pprint.PrettyPrinter(indent=4)

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")


for var in os.environ:
    routes = {}
    filters = {}
    if var.startswith("SC4S_DEST_") and var.endswith("_FILTERED_ALTERNATES"):
        dest_key = var.replace("SC4S_DEST_", "").replace("_FILTERED_ALTERNATES", "")
        dest_key_dests = os.environ[var].split(",")
        dest_filters = os.getenv(
            f"SC4S_DEST_{ dest_key }_ALT_FILTER", "f_is_nevermatch"
        ).split(",")
        # create a list of all the dests
        pairs = []
        filters = {}
        for i in range(0, len(dest_key_dests)):
            d = dest_key_dests[i]
            # dest_key_dests[i]
            if len(dest_filters) == 1:
                f = dest_filters[0]
            else:
                f = dest_filters[i]

            if f in filters.keys():
                filters[f].append(d)
            else:
                filters[f] = [d]
        msg = tm.render(dest_key=dest_key, filters=filters)
        print(msg)

#! /usr/bin/env python3
import os
import jinja2

plugin_path = os.path.dirname(os.path.abspath(__file__))

templateLoader = jinja2.FileSystemLoader(searchpath=plugin_path)
templateEnv = jinja2.Environment(loader=templateLoader)
tm = templateEnv.get_template("plugin.jinja")

routes = {}

for var in os.environ:
    if (
        var.startswith("SC4S_DEST_")
        and var.endswith("_ALTERNATES")
        and not var.endswith("_FILTERED_ALTERNATES")
    ):
        dest_key = var.replace("SC4S_DEST_", "").replace("_ALTERNATES", "")
        dest_key_dests = os.environ[var].split(",")

        # create a list of all the dests
        for dd in dest_key_dests:
            if not dd in routes.keys():
                routes[dd] = []
            if not dest_key in routes[dd]:
                routes[dd].append(dest_key)

for d in routes.keys():
    msg = tm.render(destination=d, set=f'(^|,){ "|".join(routes[d]) }(,|$)')
    print(msg)

#! /usr/bin/env python3
import os
from jinja2 import Template

template = """
log{
    filter {
        match('{{ set }}' value('.dest_key'))
    };
    destination({{ destination }});
    flags(catchall);
};

"""
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


tm = Template(template)
for d in routes.keys():
    msg = tm.render(destination=d, set=f'(^|,){ "|".join(routes[d]) }(,|$)')
    print(msg)

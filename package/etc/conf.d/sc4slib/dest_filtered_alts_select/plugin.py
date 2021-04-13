#! /usr/bin/env python3
import os
from jinja2 import Template

template = """
log{
    filter {
        ("${.dest_key}" eq "{{ filters[0][0] }}" and filter({{ filters[0][1] }}) )
        {%- for i in range(1, fcount ) %}
        or ("${.dest_key}" eq "{{ filters[i][0] }}" and filter({{ filters[i][1] }}) )
        {%- endfor %}
    };
    destination({{ destination }});
    flags(catchall);
};

"""
routes = {}
filters = {}
for var in os.environ:
    if var.startswith("SC4S_DEST_") and var.endswith("_FILTERED_ALTERNATES"):
        dest_key = var.replace("SC4S_DEST_", "").replace("_FILTERED_ALTERNATES", "")
        dest_key_dests = os.environ[var].split(",")

        # create a list of all the dests
        for dd in dest_key_dests:
            if not dd in routes.keys():
                routes[dd] = []
            if not dest_key in routes[dd]:
                routes[dd].append(dest_key)

        filters[dest_key] = os.getenv(
            f"SC4S_DEST_{ dest_key }_ALT_FILTER", "f_is_nevermatch"
        )
        filter_list = []
        for df in filters.keys():
            filter_list.append([df,filters[df]])
    
tm = Template(template)
for d in routes.keys():
    msg = tm.render(destination=d, filters=filter_list, fcount=len(filter_list))
    print(msg)

#! /usr/bin/env python3
import os
from jinja2 import Template

template = """
log{
    destination({{ destination }});
    flags(catchall);
};

"""

tm = Template(template)
if os.getenv("SC4S_DEST_GLOBAL_ALTERNATES"):
    for d in os.getenv("SC4S_DEST_GLOBAL_ALTERNATES").split(","):
        msg = tm.render(destination=d)
        print(msg)



#! /usr/bin/env python3
import os
from jinja2 import Template

template = """
source s_snmp {
    channel {
        source {
            snmptrap(
                filename("`SC4S_VAR`/log/snmptrapd.log")
            );
        };

        rewrite { r_set_splunk_dest_default(
            index('main')
            sourcetype("snmp:trap")
            vendor_product('snmp_trap')
            template('t_snmp_trap')
            ) 
        };

        parser {p_add_context_splunk(); };
        parser (compliance_meta_by_source);    
    };
 };

"""

tm = Template(template)
if os.getenv("SC4S_SNMP_TRAP_COLLECT") == "yes":
    msg = tm.render()
    print(msg)

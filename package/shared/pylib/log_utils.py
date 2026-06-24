"""
Utility functions for working with syslog-ng LogMessage objects.
"""

import json
from typing import Dict


def log_message_to_dict(log_message) -> Dict:
    """
    Convert a syslog-ng LogMessage to a Python dictionary.
    
    Args:
        log_message: syslog-ng LogMessage object
    
    Returns:
        dict: Dictionary containing all key-value pairs from the log message
    """
    result = {}
    for key in log_message.keys():
        if isinstance(key, bytes):
            key_str = key.decode("utf-8")
        else:
            key_str = key
        result[key_str] = log_message.get_as_str(key)
    return result

def format_log_message(log_message) -> str:
    return json.dumps(log_message_to_dict(log_message), indent=2)
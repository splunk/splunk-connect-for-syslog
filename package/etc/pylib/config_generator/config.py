import os
from pathlib import Path
from dataclasses import dataclass
from typing import List
import logging

import yaml


logger = logging.getLogger(__name__)


@dataclass
class Config:
    addons: List[str]
    addons_path: Path = Path(os.path.expandvars("${SC4S_ETC}/addons"))
    syslog_path: Path = Path(os.path.expandvars("${SC4S_ETC}/syslog-ng.conf.jinja"))


def load_addons_config(config_path: Path) -> Config:
    with open(config_path, "r") as file_stream:
        try:
            raw_config = yaml.safe_load(file_stream)
            return Config(**raw_config)
        except yaml.YAMLError:
            logger.error("Config should be correct yaml")
        except KeyError:
            logger.error("Field is missing in config")
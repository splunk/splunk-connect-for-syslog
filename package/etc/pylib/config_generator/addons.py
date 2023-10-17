import os
from logging import getLogger
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml


logger = getLogger(__name__)


@dataclass
class AddonMetada:
    name: str


@dataclass
class Addon:
    path: Path
    metadata: AddonMetada


def load_addons(addons_directory: Path) -> List[Addon]:
    addons: List[Addon] = []

    for potential_addon in os.listdir(addons_directory):
        addon_full_path = addons_directory / potential_addon

        if (
            os.path.isdir(addon_full_path) and
            "addon_metadata.yaml" in os.listdir(addon_full_path)
        ):
            try:
                metadata = load_addon_metadata(addon_full_path)
                addons.append(Addon(path=addon_full_path, metadata=metadata))
            except Exception:
                logger.error(f"Skipping invalid addon {potential_addon}")

    return addons


def load_addon_metadata(addon_path: Path) -> AddonMetada:
    with open(addon_path / "addon_metadata.yaml", "r") as file_stream:
        try:
            metadata = yaml.safe_load(file_stream)
            return AddonMetada(name=metadata["name"])
        except yaml.YAMLError:
            logger.error(f"Metadata file of {addon_path} should be valid yaml")
        except KeyError:
            logger.error(f"Missing metadata in {addon_path}")

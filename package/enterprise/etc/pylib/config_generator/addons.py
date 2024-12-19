from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

import yaml


logger = getLogger(__name__)


@dataclass
class AddonMetadata:
    name: str


@dataclass
class Addon:
    path: Path
    metadata: AddonMetadata


def load_addons(addons_directory: Path) -> list[Addon]:
    addons: list[Addon] = []

    for potential_addon in addons_directory.iterdir():
        addon_full_path = addons_directory / potential_addon

        if (
            addon_full_path.is_dir() and
            (addon_full_path / "addon_metadata.yaml").exists()
        ):
            try:
                metadata = load_addon_metadata(addon_full_path)
                addons.append(Addon(path=addon_full_path, metadata=metadata))
            except Exception as e:
                logger.error(f"Skipping invalid addon {potential_addon}")
                raise e

    return addons


def load_addon_metadata(addon_path: Path) -> AddonMetadata:
    with open(addon_path / "addon_metadata.yaml", "r") as file_stream:
        try:
            metadata = yaml.safe_load(file_stream)
            return AddonMetadata(name=metadata["name"])
        except yaml.YAMLError:
            logger.error(f"Metadata file of {addon_path} should be valid yaml")
        except KeyError:
            logger.error(f"Missing metadata in {addon_path}")

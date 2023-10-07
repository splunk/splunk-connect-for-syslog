from pathlib import Path
import argparse

from .config import load_addons_config
from .addons import load_addons
from .template_generator import template_generator


def parse_cli_args():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument("--config", type=Path)
    return cli_parser.parse_args()


def generate_syslogng_config() -> None:
    cli_args = parse_cli_args()
    config = load_addons_config(cli_args.config)
    addons = load_addons(config.addons_path)

    syslogng_config = template_generator(
        config.syslog_path,
        config=config,
        addons=addons,
    )
    print(syslogng_config)


if __name__ == "__main__":
    generate_syslogng_config()

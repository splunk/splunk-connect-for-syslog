import collections
import os
import logging


logger = logging.getLogger(__name__)


def is_valid_port(raw_port: str) -> bool:
    return raw_port.isdigit() and 0 < int(raw_port) < 65565


def validate_source_ports(sources: list[str]) -> None:
    source_ports = {}
    for source in sources:
        for proto in ["TCP", "UDP", "TLS", "RFC5426", "RFC6587", "RFC5425"]:
            source_ports[(source, proto)] = os.getenv(f"SC4S_LISTEN_{source}_{proto}_PORT", "disabled").split(",")


    busy_ports_for_proto = collections.defaultdict(set)
    for source, proto in source_ports.keys():        
        for port in source_ports[(source, proto)]:
            if not port or port == "disabled":
                continue

            elif not is_valid_port(port):
                logger.error(f"SC4S_LISTEN_{source}_{proto}_PORT: {port} must be integer within the range (0, 65565)")

            elif source != "DEFAULT" and port in source_ports[("DEFAULT", proto)]:
                logger.error(f"SC4S_LISTEN_{source}_{proto}_PORT: Wrong {port} number, don't use default port like {port}")

            elif port in busy_ports_for_proto[proto]:
                logger.error(f"SC4S_LISTEN_{source}_{proto}_PORT: {port} is not unique and has already been used for another source")

            else:
                busy_ports_for_proto[proto].add(port)


if __name__ == "__main__":
    sources = os.getenv("SOURCE_ALL_SET").split(",")
    validate_source_ports(sources)

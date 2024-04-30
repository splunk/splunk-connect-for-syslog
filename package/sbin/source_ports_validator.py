import os
import logging


logger = logging.getLogger(__name__)


def is_valid_port(raw_port: str) -> bool:
    return raw_port.isdigit() and int(raw_port) < 10000


def validate_source_ports(sources: list[str]) -> None:
    source_ports = []
    for source in sources:
        tcp_ports = os.getenv(f"SC4S_LISTEN_{source}_TCP_PORT", "disabled").split(",")
        udp_ports = os.getenv(f"SC4S_LISTEN_{source}_UDP_PORT", "disabled").split(",")
        tls_ports = os.getenv(f"SC4S_LISTEN_{source}_TLS_PORT", "disabled").split(",")

        source_ports.extend((source, port, "TCP") for port in tcp_ports)
        source_ports.extend((source, port, "UDP") for port in udp_ports)
        source_ports.extend((source, port, "TLS") for port in tls_ports)


    busy_ports = set()
    for source, port, proto in source_ports:
        env_var = f"SC4S_LISTEN_{source}_{port}_PORT"

        if port in ["disabled", ""]:
            continue
        elif not is_valid_port(port):
            logger.error(f"{env_var}: {port} must be integer within the range (0, 10000). Update {env_var} value")
        elif source != "DEFAULT" and port in ["514", "614", "6514"]:
            logger.error(f"{env_var}: Wrong port number, don't use default port like (514,614,6514). Update {env_var} value")
        elif (port, proto) in busy_ports:
            logger.error(f"{env_var}: {port} is not unique and has already been used for another source. Update {env_var} value")
        else:
            busy_ports.add((port, proto))


if __name__ == "__main__":
    sources = os.getenv("SOURCE_ALL_SET").split(",")
    validate_source_ports(sources)

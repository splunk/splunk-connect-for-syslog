from enum import Enum
import logging
import os


logger = logging.getLogger(__name__)

class TransportMode(Enum):
    HTTP = "http"
    STDIO = "stdio"

def resolve_transport() -> TransportMode:
    env = os.environ.get("MCP_TRANSPORT")
    if env:
        env = env.strip().lower()
        if env == "http":
            return TransportMode.HTTP
        if env == "stdio":
            return TransportMode.STDIO
        logger.info("MCP_TRANSPORT=%r not recognized, defaulting to STDIO", env)
        return TransportMode.STDIO
    logger.info("MCP_TRANSPORT empty using STDIO")
    return TransportMode.STDIO
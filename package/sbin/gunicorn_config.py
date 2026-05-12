"""Gunicorn configuration file for the SC4S management API.

Loaded via ``gunicorn --config gunicorn_config``. Applies TLS settings when
SC4S_API_TLS_CERT and SC4S_API_TLS_KEY are set; otherwise serves plain HTTP.
"""

import logging
import sys

from tls import TlsConfigError, build_gunicorn_ssl_kwargs, tls_is_enabled

logger = logging.getLogger(__name__)

try:
    _ssl_kwargs = build_gunicorn_ssl_kwargs()
except TlsConfigError as exc:
    logger.error("Management API TLS configuration error: %s", exc)
    sys.exit(1)

if _ssl_kwargs:
    certfile = _ssl_kwargs["certfile"]
    keyfile = _ssl_kwargs["keyfile"]
    keyfile_password = _ssl_kwargs["keyfile_password"]
    logger.info("Management API TLS enabled")

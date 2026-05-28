"""Opt-in TLS configuration for the SC4S management API.

TLS is enabled when both ``SC4S_API_TLS_CERT`` and ``SC4S_API_TLS_KEY``
environment variables point to readable PEM files. ``SC4S_API_TLS_KEY_PASSWORD``
is optional. Plaintext HTTP remains the default behavior when no TLS env vars
are set.
"""

import os
from typing import Any

TLS_CERT_ENV = "SC4S_API_TLS_CERT"
TLS_KEY_ENV = "SC4S_API_TLS_KEY"
TLS_KEY_PASSWORD_ENV = "SC4S_API_TLS_KEY_PASSWORD"


class TlsConfigError(RuntimeError):
    """Raised when TLS env vars are misconfigured (e.g. only one of cert/key set)."""


def tls_is_enabled() -> bool:
    """Return ``True`` when both cert and key env vars are set to non-empty values."""
    cert = (os.environ.get(TLS_CERT_ENV) or "").strip()
    key = (os.environ.get(TLS_KEY_ENV) or "").strip()
    return bool(cert) and bool(key)


def build_gunicorn_ssl_kwargs() -> dict[str, Any]:
    """Build the SSL kwargs to pass to Gunicorn.

    Returns an empty dict when TLS is disabled (both env vars unset or blank).
    Raises :class:`TlsConfigError` when exactly one of cert/key is set.
    The returned dict uses Gunicorn's ``certfile`` / ``keyfile`` / ``keyfile_password`` keys.
    """
    cert_path = (os.environ.get(TLS_CERT_ENV) or "").strip()
    key_path = (os.environ.get(TLS_KEY_ENV) or "").strip()
    password = os.environ.get(TLS_KEY_PASSWORD_ENV)

    if not cert_path and not key_path:
        return {}

    if bool(cert_path) != bool(key_path):
        missing = TLS_KEY_ENV if not key_path else TLS_CERT_ENV
        provided = TLS_CERT_ENV if cert_path else TLS_KEY_ENV
        raise TlsConfigError(
            f"TLS misconfigured: {provided} is set but {missing} is not. "
            "Set both to enable TLS, or unset both to serve plaintext HTTP."
        )

    return {
        "certfile": cert_path,
        "keyfile": key_path,
        "keyfile_password": password,
    }

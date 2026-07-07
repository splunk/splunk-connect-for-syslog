import sys

from tls import TlsConfigError, build_gunicorn_ssl_kwargs


def on_starting(server):
    if server.cfg.workers != 1:
        server.log.error(
            "Management API requires workers=1 (in-process job manager); got %s",
            server.cfg.workers,
        )
        sys.exit(1)

    try:
        ssl_kwargs = build_gunicorn_ssl_kwargs()
    except TlsConfigError as exc:
        server.log.error("Management API TLS configuration error: %s", exc)
        sys.exit(1)

    if ssl_kwargs:
        server.cfg.set("certfile", ssl_kwargs["certfile"])
        server.cfg.set("keyfile", ssl_kwargs["keyfile"])
        if ssl_kwargs["keyfile_password"] is not None:
            server.cfg.set("keyfile_password", ssl_kwargs["keyfile_password"])
        server.log.info("Management API TLS enabled")

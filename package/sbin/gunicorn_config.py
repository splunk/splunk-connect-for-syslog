import os
import ssl
import sys

from tls import TLS_KEY_PASSWORD_ENV, TlsConfigError, build_gunicorn_ssl_kwargs


def ssl_context(conf, default_ssl_context_factory):
    password = os.environ.get(TLS_KEY_PASSWORD_ENV)
    if password is None:
        return default_ssl_context_factory()

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=conf.ca_certs)
    context.load_cert_chain(
        certfile=conf.certfile, keyfile=conf.keyfile, password=password
    )
    context.verify_mode = conf.cert_reqs
    if conf.ciphers:
        context.set_ciphers(conf.ciphers)
    return context


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
        server.log.info("Management API TLS enabled")

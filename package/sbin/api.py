import logging
import os

from flask import Flask, jsonify, request

from config_api import config_bp, csrf
from healthcheck import healthcheck_bp, str_to_bool
from metadata_api import metadata_bp
from auth import build_token_verify
from tls import tls_is_enabled

logging.basicConfig(
    format="%(asctime)s - sc4s-api - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
    force=True,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
csrf.init_app(app)
app.register_blueprint(healthcheck_bp)

MANAGEMENT_ENABLED_ENV = "SC4S_API_MANAGEMENT_ENABLED"
management_enabled = str_to_bool(os.environ.get(MANAGEMENT_ENABLED_ENV, ""))

if management_enabled:
    app.register_blueprint(config_bp)
    csrf.exempt(metadata_bp)
    app.register_blueprint(metadata_bp)
    logger.info(
        "Management API endpoints enabled (%s=true): /config/* routes registered",
        MANAGEMENT_ENABLED_ENV,
    )
else:
    logger.info(
        "Management API endpoints disabled (%s unset/false); only /health is exposed",
        MANAGEMENT_ENABLED_ENV,
    )

token_verifier = build_token_verify()

if tls_is_enabled():
    logger.info("Management API TLS enabled")

PUBLIC_PATHS = ["/health"]


@app.before_request
def authenticate_user():
    if request.path in PUBLIC_PATHS:
        return None

    if token_verifier is None:
        return None

    auth_header = request.headers.get("Authorization")
    parts = auth_header.split() if auth_header else []
    presented = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else ""

    if not presented or not token_verifier.verify_token(presented):
        logger.warning(
            "Authentication failed: %s %s from %s",
            request.method,
            request.path,
            request.remote_addr,
        )
        return jsonify({"error": "Unauthorized"}), 401


HEALTHCHECK_PORT = int(os.getenv("SC4S_LISTEN_STATUS_PORT", "8080"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HEALTHCHECK_PORT)

import logging
import os

from flask import Flask, jsonify, request

from config_api import config_bp, csrf
from healthcheck import healthcheck_bp
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
app.register_blueprint(config_bp)
csrf.exempt(metadata_bp)
app.register_blueprint(metadata_bp)

tokenVerifier = build_token_verify()

if tls_is_enabled():
    logger.info("Management API TLS enabled")

PUBLIC_PATHS = ["/health"]

@app.before_request
def authenticate_user():
    if request.path in PUBLIC_PATHS:
        return None

    if tokenVerifier is None:
        return None

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401

    splitted = auth_header.split()

    if len(splitted) != 2 or splitted[0].lower() != 'bearer':
        return jsonify({'error': 'Invalid Authorization format. Expected: Bearer <token>'}), 401

    presented = splitted[1]
    
    if not tokenVerifier.verify_token(presented):
        logger.warning(
            "Authentication failed: %s %s from %s",
            request.method,
            request.path,
            request.remote_addr,
        )
        return jsonify({'error': 'Authentication failed'}), 401

HEALTHCHECK_PORT = int(os.getenv("SC4S_LISTEN_STATUS_PORT", "8080"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HEALTHCHECK_PORT)

import logging
import os
from re import I

from flask import Flask, jsonify, request

from config_api import config_bp, csrf
from healthcheck import healthcheck_bp
from metadata_api import metadata_bp
from package.sbin.auth import build_token_verify

logging.basicConfig(
    format="%(asctime)s - sc4s-api - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)
csrf.init_app(app)
app.register_blueprint(healthcheck_bp)
app.register_blueprint(config_bp)
csrf.exempt(metadata_bp)
app.register_blueprint(metadata_bp)

tokenVerifier = build_token_verify()

PUBLIC_PATHS = ["/health"]

@app.before_request
def authenticate_user():
    if request.path in PUBLIC_PATHS:
        return None

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({'error': 'Missing Authorization header'}), 401

    splitted = auth_header.split()

    if len(splitted) != 2 or splitted[0].lower() != 'bearer':
        return jsonify({'error': 'Invalid Authorization format. Expected: Bearer <token>'}), 401

    presented = splitted[1]
    
    tokenVerifier.verify_token(presented)

HEALTHCHECK_PORT = int(os.getenv("SC4S_LISTEN_STATUS_PORT", "8080"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HEALTHCHECK_PORT)

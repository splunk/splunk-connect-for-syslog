import logging
import os

from flask import Flask

from config_api import config_bp, csrf
from healthcheck import healthcheck_bp

logging.basicConfig(
    format="%(asctime)s - sc4s-api - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)
csrf.init_app(app)
app.register_blueprint(healthcheck_bp)
app.register_blueprint(config_bp)

HEALTHCHECK_PORT = int(os.getenv("SC4S_LISTEN_STATUS_PORT", "8080"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=HEALTHCHECK_PORT)

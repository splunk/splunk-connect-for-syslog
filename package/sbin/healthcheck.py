from flask import Flask, jsonify
import logging
import os
import subprocess

app = Flask(__name__)

class Config:
    SC4S_DEST_SPLUNK_HEC_DEFAULT_URL = os.getenv('SC4S_DEST_SPLUNK_HEC_DEFAULT_URL')
    HEALTHCHECK_PORT = int(os.getenv('SC4S_LISTEN_STATUS_PORT', '8080'))
    CHECK_QUEUE_SIZE = bool(os.getenv('HEALTHCHECK_CHECK_QUEUE_SIZE', False))
    MAX_QUEUE_SIZE = int(os.getenv('HEALTHCHECK_MAX_QUEUE_SIZE', '10000'))

logger = logging.getLogger(__name__)

def check_syslog_ng_health() -> bool:
    """Check the health of the syslog-ng process."""
    try:
        result = subprocess.run(
            ['syslog-ng-ctl', 'healthcheck', '-t', '1'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
        
        logger.error(f"syslog-ng healthcheck failed: {result.stderr.strip()}")
        return False
    except subprocess.TimeoutExpired:
        logger.error("syslog-ng healthcheck timed out.")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during syslog-ng healthcheck: {e}")
        return False

def check_queue_size() -> bool:
    """Check syslog-ng queue size and compare it against the configured maximum limit."""
    if not Config.SC4S_DEST_SPLUNK_HEC_DEFAULT_URL:
        logger.error(
            "SC4S_DEST_SPLUNK_HEC_DEFAULT_URL not configured. "
            "Ensure the default HEC destination is set, or disable HEALTHCHECK_CHECK_QUEUE_SIZE."
        )
        return False

    try:
        result = subprocess.run(
            ['syslog-ng-ctl', 'stats'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            logger.error(f"syslog-ng stats command failed: {result.stderr.strip()}")
            return False

        stats = result.stdout.splitlines()
        destination_stat = next(
            (s for s in stats if ";queued;" in s and Config.SC4S_DEST_SPLUNK_HEC_DEFAULT_URL in s),
            None
        )
        if not destination_stat:
            logger.error("No matching queue stats found for the destination URL.")
            return False

        queue_size = int(destination_stat.split(";")[-1])
        if queue_size > Config.MAX_QUEUE_SIZE:
            logger.warning(
                f"Queue size {queue_size} exceeds the maximum limit of {Config.MAX_QUEUE_SIZE}."
            )
            return False

        return True
    except subprocess.TimeoutExpired:
        logger.error("syslog-ng stats command timed out.")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error checking queue size: {e}")
        return False

@app.route('/health', methods=['GET'])
def healthcheck():
    if Config.CHECK_QUEUE_SIZE:
        if not check_syslog_ng_health():
            return jsonify({'status': 'unhealthy: syslog-ng healthcheck failed'}), 503
        if not check_queue_size():
            return jsonify({'status': 'unhealthy: queue size exceeded limit'}), 503
    else:
        if not check_syslog_ng_health():
            return jsonify({'status': 'unhealthy: syslog-ng healthcheck failed'}), 503

    logger.info("Service is healthy.")
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.HEALTHCHECK_PORT)
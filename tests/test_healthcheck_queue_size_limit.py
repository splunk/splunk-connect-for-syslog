import argparse
import socket
import sys
from time import time
import requests

def send_messages(host, port, message, limit):
    for _ in range(limit):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            sock.sendall(message.encode())

def check_health(host, port):
    try:
        response = requests.get(f"http://{host}:{port}/health")
        return response.json()
    except requests.RequestException as e:
        print(f"Error checking health endpoint: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Test queue size limit for health checking in SC4S.")
    parser.add_argument("--limit", type=int, required=True, help="Number of messages to send.")
    parser.add_argument("--host", type=str, required=True, help="Host of the SC4S server.")
    parser.add_argument("--port", type=int, required=True, help="Port for the health check endpoint.")
    parser.add_argument("--udp-port", type=int, default=514, help="UDP port to send messages to (default: 514).")

    args = parser.parse_args()

    print(f"Sending {args.limit} messages to {args.host}:{args.udp_port}...")
    send_messages(args.host, args.udp_port, "message", args.limit)

    time.sleep(1)  # time to save the messages
    print(f"Checking health status on {args.host}:{args.port}...")
    health_status = check_health(args.host, args.port)

    if health_status.get("status") == "unhealthy: queue size exceeded limit":
        print("Queue size limit works.")
    else:
        print("Queue size limit doesn't work.")
        sys.exit(1)

if __name__ == "__main__":
    main()

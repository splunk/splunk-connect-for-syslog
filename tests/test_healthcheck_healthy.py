import argparse
import time
import requests
import sys

def check_service_health(host, port, retries=12, delay=10):
    url = f"http://{host}:{port}/health"
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200 and response.json().get("status") == "healthy":
                print("Service is healthy.")
                return
            else:
                print(f"Attempt {attempt}/{retries}: unexpected response: {response.text}")
        except requests.RequestException as e:
            print(f"Attempt {attempt}/{retries}: {e}")
        if attempt < retries:
            time.sleep(delay)
    print("Service health check failed after all retries.")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="SC4S Service Health Check")
    parser.add_argument("--host", required=True, help="Host address of the SC4S service")
    parser.add_argument("--port", required=True, type=int, help="Port number of the SC4S service")
    
    args = parser.parse_args()
    check_service_health(args.host, args.port)


if __name__ == "__main__":
    main()

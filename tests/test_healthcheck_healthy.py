import argparse
import requests
import sys

def check_service_health(host, port):
    url = f"http://{host}:{port}/health"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("Service is healthy.")
        else:
            print(f"Service health check failed. Response: {response.text}")
            sys.exit(1)
    except requests.RequestException as e:
        print(f"Service health check failed. Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="SC4S Service Health Check")
    parser.add_argument("--host", required=True, help="Host address of the SC4S service")
    parser.add_argument("--port", required=True, type=int, help="Port number of the SC4S service")
    
    args = parser.parse_args()
    check_service_health(args.host, args.port)


if __name__ == "__main__":
    main()

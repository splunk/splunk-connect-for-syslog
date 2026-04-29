import json
import os
import platform
import subprocess
from datetime import datetime

import requests
import urllib3


def subprocess_command_executor(command_string):
    try:
        result = subprocess.run(
            command_string, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error code {e.returncode}")
        print(f"Stdout: {e.stdout.strip()}")
        print(f"Stderr: {e.stderr.strip()}")
    except FileNotFoundError:
        print("Error: The shell or a command within the pipeline was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_os_values() -> dict:
    try:
        command_string = "cat /etc/*-release"
        os_text_data = subprocess_command_executor(command_string)
        os_dict = dict()
        for line in os_text_data.replace('"', "").split("\n"):
            try:
                key, val = line.split("=")
            except ValueError:
                continue
            else:
                os_dict[key.strip()] = val.strip()
        return os_dict
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_physical_cpu_cores():
    try:
        command_string = "nproc"
        return subprocess_command_executor(command_string)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_runtime_environment():
    try:
        command_string = '[ -f /.dockerenv ] && echo "docker" || echo "unknown"'
        return subprocess_command_executor(command_string)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def detect_app_version() -> str:
    sc4s_etc = os.environ.get("SC4S_ETC", "/etc/syslog-ng")
    try:
        with open(os.path.join(sc4s_etc, "VERSION"), "r", encoding="utf-8") as f:
            version = f.read().strip()
            return version or "unknown"
    except OSError:
        return "unknown"


def detect_app_edition() -> str:
    sc4s_etc = os.environ.get("SC4S_ETC", "/etc/syslog-ng")
    if os.path.exists(os.path.join(sc4s_etc, "syslog-ng.conf.jinja")):
        return "lite"
    if os.path.exists(os.path.join(sc4s_etc, "syslog-ng.conf")):
        return "base"
    return "unknown"


def detect_container_engine() -> str:
    container_env = os.environ.get("container", "").lower()
    if container_env == "podman":
        return "podman"

    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "containerd"

    try:
        with open("/proc/1/cgroup", "r", encoding="utf-8") as f:
            cgroup = f.read()
    except OSError:
        cgroup = ""

    if "kubepods" in cgroup:
        return "containerd"
    if "libpod" in cgroup:
        return "podman"
    if "/docker/" in cgroup or "docker-" in cgroup:
        return "docker"

    if os.path.exists("/.dockerenv"):
        return "docker"

    return "unknown"


def telemetry_data_collector():
    os_values = get_os_values()
    payload_data = {
        "datetime": str(datetime.now()),
        "app_name": "sc4s",
        "app_version": detect_app_version(),
        "app_edition": detect_app_edition(),
        "os_name": os_values.get("NAME", "unknown"),
        "os_version": os_values.get("VERSION_ID", "unknown"),
        "os_release": os_values.get("VERSION", "unknown"),
        "kernel_name": platform.system() or "unknown",
        "kernel_version": platform.uname().version or "unknown",
        "kernel_release": platform.uname().release or "unknown",
        "cpu_architecture": platform.uname().machine or "unknown",
        "cpu_count": get_physical_cpu_cores() or "unknown",
        "container_engine": detect_container_engine(),
        "runtime_environment": get_runtime_environment() or "unknown",
        "runtime_version": "unknown",
        "runtime_mode": "unknown",
        "runtime_base_os_name": os_values.get("NAME", "unknown"),
        "runtime_base_os_version": os_values.get("VERSION_ID", "unknown"),
        "runtime_base_os_release": os_values.get("VERSION", "unknown"),
        "orchestrator": "unknown",
    }

    return payload_data


def main():
    # print("telemetry_data_collector := ")
    # print(telemetry_data_collector())

    # Environment variables (same as in your shell)
    SC4S_DEST_SPLUNK_HEC_DEFAULT_URL = os.getenv("HEC")
    SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN = os.getenv("SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN")
    SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX = os.getenv(
        "SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX"
    )

    # Prepare headers and payload
    headers = {
        "Authorization": f"Splunk {SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN}",
        "Content-Type": "application/json",
    }

    telemetry_data = telemetry_data_collector()
    payload = {
        "event": telemetry_data,
        "sourcetype": "sc4s:probe",
        "index": SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX,
    }

    print(f"{SC4S_DEST_SPLUNK_HEC_DEFAULT_URL = }")
    print(f"{SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN = }")
    print(f"{headers = }")
    print(f"{payload = }")

    # Send the request
    try:
        import code

        code.interact(local=dict(globals(), **locals()))

        response = requests.post(
            SC4S_DEST_SPLUNK_HEC_DEFAULT_URL,
            headers=headers,
            data=json.dumps(payload),
            verify=False,
        )
        print(f"Status: {response.status_code}")
        print(response.text)
    except requests.RequestException as e:
        print(f"Error sending event: {e}")


if __name__ == "__main__":
    main()

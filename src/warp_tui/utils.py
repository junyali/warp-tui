import subprocess
from enum import Enum

# TODO: don't hardcode this silly
polling_rate = 0.5 # seconds

class State(Enum):
    CONNECTED = "Connected"
    CONNECTING = "Connecting"
    DISCONNECTED = "Disconnected"
    TIMEOUT = "Timeout"
    ERROR = "Error"
    UNKNOWN = "Unknown"

class WarpCLI:
    @staticmethod
    def get_status():
        try:
            result = subprocess.run(
                ["warp-cli", "status"],
                capture_output=True,
                text=True,
                timeout=5
            )

            status = None
            reason = None

            for line in result.stdout.splitlines():
                if line.startswith("Status update:"):
                    status = line.split("Status update:")[1].strip()
                elif line.startswith("Reason:"):
                    reason = line.split("Reason:")[1].strip()

            return status, reason
        except subprocess.TimeoutExpired:
            return "Timeout", None
        except Exception as e:
            return "Error", str(e)

    @staticmethod
    def get_mode():
        try:
            result = subprocess.run(
                ["warp-cli", "settings", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.splitlines():
                if "Mode:" in line:
                    mode_text = line.split("Mode:")[1].strip()
                    if mode_text.startswith("WarpProxy"):
                        return "WarpProxy"
                    mode_map = {
                        "Warp": "warp",
                        "DnsOverHttps": "doh",
                        "WarpWithDnsOverHttps": "warp+doh",
                        "DnsOverTls": "dot",
                        "WarpWithDnsOverTls": "warp+dot",
                        "WarpProxy": "proxy",
                        "TunnelOnly": "tunnel_only",
                    }
                    return mode_map.get(mode_text)
            return None
        except Exception:
            return None

    @staticmethod
    def set_mode(mode: str):
        try:
            result = subprocess.run(
                ["warp-cli", "mode", mode],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            return str(e)

    @staticmethod
    def get_proxy_port():
        try:
            result = subprocess.run(
                ["warp-cli", "settings", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.splitlines():
                if "Mode:" in line and "WarpProxy" in line:
                    parts = line.split("port")
                    if len(parts) > 1:
                        return parts[1].strip()
            return None
        except Exception:
            return None

    @staticmethod
    def set_proxy_port(port: str):
        try:
            result = subprocess.run(
                ["warp-cli", "proxy", "port", port],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode
        except Exception as e:
            return str(e)

    @staticmethod
    def connect():
        try:
            result = subprocess.run(
                ["warp-cli", "connect"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode
        except Exception as e:
            return str(e)

    @staticmethod
    def disconnect():
        try:
            result = subprocess.run(
                ["warp-cli", "disconnect"],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode
        except Exception as e:
            return str(e)

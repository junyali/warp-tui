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

    @staticmethod
    def check_registration():
        try:
            result = subprocess.run(
                ["warp-cli", "registration", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout + result.stderr
            return not ("Missing registration" in output or "Missing registration" in output)
        except Exception:
            return False

    @staticmethod
    def get_registration_info():
        try:
            result = subprocess.run(
                ["warp-cli", "registration", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()

            return output, result.returncode == 0
        except Exception as e:
            return f"Error: {str(e)}", False

    @staticmethod
    def register_new():
        try:
            result = subprocess.run(
                ["warp-cli", "registration", "new"],
                capture_output=True,
                text=True,
                timeout=30
            )
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return result.returncode == 0, error_msg
        except Exception as e:
            return False, str(e)

    @staticmethod
    def delete_registration():
        try:
            result = subprocess.run(
                ["warp-cli", "registration", "delete"],
                capture_output=True,
                text=True,
                timeout=10
            )
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return result.returncode == 0, error_msg
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_devices():
        try:
            result = subprocess.run(
                ["warp-cli", "registration", "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()

            return output, result.returncode == 0
        except Exception as e:
            return f"Error: {str(e)}", False

    @staticmethod
    def dump_tunnel():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "dump"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()

            return output, result.returncode == 0
        except Exception as e:
            return f"Error: {str(e)}", False

    @staticmethod
    def get_stats():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "stats"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()

            if "not connected" in output:
                return output, False
            else:
                return output, result.returncode == 0
        except Exception as e:
            return f"Error: {str(e)}", False

    @staticmethod
    def rotate_keys():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "rotate-keys"],
                capture_output=True,
                text=True,
                timeout=30
            )
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return result.returncode == 0, error_msg
        except Exception as e:
            return False, str(e)

    @staticmethod
    def set_endpoint(sockaddr: str):
        try:
            if ":" not in sockaddr:
                return False, "Invalid socket address syntax"

            parts = sockaddr.split(":")
            if len(parts) != 2:
                return False, "Invalid socket address syntax"

            ip, port = parts

            if not port.isdigit():
                return False, "Invalid socket address syntax"

            port_num = int(port)
            if not (1 <= port_num <= 65535):
                return False, "Invalid socket address syntax"

            ip = ip.strip()
            if not ip:
                return False, "Invalid socket address syntax"

            result = subprocess.run(
                ["warp-cli", "tunnel", "endpoint", "set", sockaddr],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def reset_endpoint():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "endpoint", "reset"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def set_protocol(protocol: str):
        try:
            if protocol not in ["MASQUE", "WireGuard"]:
                return False, "Invalid protocol"

            result = subprocess.run(
                ["warp-cli", "tunnel", "protocol", "set", protocol],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def reset_protocol():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "protocol", "reset"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def set_masque(protocol: str):
        try:
            if protocol not in ["h3-only", "h2-only", "h3-with-h2-fallback"]:
                return False, "Invalid MASQUE protocol"

            result = subprocess.run(
                ["warp-cli", "tunnel", "masque-options", "set", protocol],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def reset_masque():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "masque-options", "reset"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def list_tunnel_host():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "host", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return output, result.returncode == 0
        except Exception as e:
            return f"Error: {str(e)}", False

    @staticmethod
    def add_tunnel_host(host: str):
        try:
            if not host or not host.strip():
                return False, "Invalid"

            result = subprocess.run(
                ["warp-cli", "tunnel", "host", "add", host],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def remove_tunnel_host(host: str):
        try:
            if not host or not host.strip():
                return False, "Invalid"

            result = subprocess.run(
                ["warp-cli", "tunnel", "host", "remove", host],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def reset_tunnel_host():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "host", "reset"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def list_tunnel_ip():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "ip", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return output, result.returncode == 0
        except Exception as e:
            return f"Error: {str(e)}", False

    @staticmethod
    def add_tunnel_ip(ip: str):
        try:
            if not ip or not ip.strip():
                return False, "Invalid"

            result = subprocess.run(
                ["warp-cli", "tunnel", "ip", "add", ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def remove_tunnel_ip(ip: str):
        try:
            if not ip or not ip.strip():
                return False, "Invalid"

            result = subprocess.run(
                ["warp-cli", "tunnel", "ip", "remove", ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

    @staticmethod
    def reset_tunnel_ip():
        try:
            result = subprocess.run(
                ["warp-cli", "tunnel", "ip", "reset"],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout.strip()
            if not output and result.stderr:
                output = result.stderr.strip()
            return result.returncode == 0, output
        except Exception as e:
            return False, str(e)

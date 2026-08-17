"""
Network Tools Module — Network diagnostics and information.
Ping, speed test, IP address, port scan, DNS lookup.
"""

import subprocess
import platform
import socket
import json

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def get_ip_address() -> str:
    """Get local and public IP addresses."""
    # Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "unknown"

    # Public IP
    public_ip = "unknown"
    if HAS_REQUESTS:
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            public_ip = response.json().get("ip", "unknown")
        except Exception:
            pass

    return f"IP Addresses:\n  Local: {local_ip}\n  Public: {public_ip}"


def ping_host(text: str) -> str:
    """Ping a host to check connectivity."""
    # Extract hostname
    host = ""
    for prefix in ["ping ", "ping host", "ping server"]:
        if prefix in text.lower():
            host = text.lower().split(prefix, 1)[-1].strip()
            break

    if not host:
        return "Which host would you like me to ping? Example: ping google.com"

    count_flag = "-c" if platform.system() != "Windows" else "-n"
    count = "4"

    try:
        result = subprocess.run(
            ["ping", count_flag, count, host],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if result.returncode == 0:
            return f"Ping results for {host}:\n{output}"
        return f"Ping failed for {host}:\n{output}"
    except subprocess.TimeoutExpired:
        return f"Ping timed out for {host}, sir."
    except Exception as e:
        return f"Error pinging {host}: {e}"


def speed_test() -> str:
    """Run a quick internet speed test."""
    if not HAS_REQUESTS:
        return "Install requests: pip install requests"

    import time

    try:
        # Download speed test (download a small file)
        start = time.time()
        response = requests.get(
            "https://speed.cloudflare.com/__down?bytes=1000000",
            timeout=30, stream=True
        )
        content = response.content
        download_time = time.time() - start
        download_speed = (len(content) * 8) / download_time / 1_000_000  # Mbps

        # Upload speed test
        start = time.time()
        requests.post(
            "https://speed.cloudflare.com/__up",
            data=b"x" * 100000,
            timeout=30
        )
        upload_time = time.time() - start
        upload_speed = (100000 * 8) / upload_time / 1_000_000  # Mbps

        return (
            f"Internet Speed Test:\n"
            f"  Download: {download_speed:.1f} Mbps\n"
            f"  Upload: {upload_speed:.1f} Mbps"
        )
    except Exception as e:
        return f"Speed test failed: {e}"


def port_scan(text: str) -> str:
    """Scan common ports on a host."""
    # Extract host
    host = ""
    for prefix in ["scan ports", "port scan", "scan "]:
        if prefix in text.lower():
            host = text.lower().split(prefix, 1)[-1].strip()
            break

    if not host:
        return "Which host would you like me to scan? Example: scan ports localhost"

    common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995,
                    3000, 3306, 5432, 6379, 8000, 8080, 8443, 9000, 27017]

    open_ports = []
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except Exception:
            continue

    if open_ports:
        port_names = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
            993: "IMAPS", 995: "POP3S", 3000: "Node/React",
            3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis",
            8000: "Alt HTTP", 8080: "Alt HTTP", 8443: "Alt HTTPS",
            9000: "PHP-FPM", 27017: "MongoDB",
        }
        result_lines = []
        for port in open_ports:
            name = port_names.get(port, "Unknown")
            result_lines.append(f"  {port:>5} - {name}")
        return f"Open ports on {host}:\n" + "\n".join(result_lines)

    return f"No common ports are open on {host}, sir."


def dns_lookup(text: str) -> str:
    """Perform a DNS lookup for a domain."""
    domain = ""
    for prefix in ["dns lookup", "lookup", "resolve", "dig "]:
        if prefix in text.lower():
            domain = text.lower().split(prefix, 1)[-1].strip()
            break

    if not domain:
        return "Which domain would you like me to look up? Example: dns lookup google.com"

    try:
        ip = socket.gethostbyname(domain)
        return f"DNS lookup for {domain}:\n  IP: {ip}"
    except socket.gaierror:
        return f"Could not resolve {domain}, sir."
    except Exception as e:
        return f"DNS lookup error: {e}"


def ping_host_wrapper(text: str) -> str:
    """Wrapper for command routing."""
    return ping_host(text)

def port_scan_wrapper(text: str) -> str:
    """Wrapper for command routing."""
    return port_scan(text)

def dns_lookup_wrapper(text: str) -> str:
    """Wrapper for command routing."""
    return dns_lookup(text)


def get_wifi_detail() -> str:
    """Get detailed Wi-Fi information (macOS)."""
    if platform.system() != "Darwin":
        return "Wi-Fi detail is only available on macOS, sir."

    try:
        # Get SSID
        result = subprocess.run(
            ["networksetup", "-getairportnetwork", "en0"],
            capture_output=True, text=True, timeout=5
        )
        ssid = result.stdout.strip()

        # Get IP
        result = subprocess.run(
            ["ipconfig", "getifaddr", "en0"],
            capture_output=True, text=True, timeout=5
        )
        ip = result.stdout.strip() or "N/A"

        # Get MAC address
        result = subprocess.run(
            ["ifconfig", "en0"],
            capture_output=True, text=True, timeout=5
        )
        mac = "N/A"
        for line in result.stdout.split("\n"):
            if "ether" in line:
                mac = line.split("ether")[-1].strip()
                break

        return f"Wi-Fi Details:\n  Network: {ssid}\n  IP: {ip}\n  MAC: {mac}"
    except Exception as e:
        return f"Error reading Wi-Fi: {e}"

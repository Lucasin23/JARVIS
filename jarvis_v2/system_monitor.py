"""
System Monitor Module — Real-time system monitoring and process management.
Gives JARVIS deep insight into your Mac's performance.
"""

import os
import platform
import subprocess
from datetime import datetime

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def get_full_system_report() -> str:
    """Comprehensive system status report."""
    if not HAS_PSUTIL:
        return "I need the 'psutil' library for system monitoring. Install it with: pip install psutil"

    # CPU info
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq()

    # Memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk
    disk = psutil.disk_usage("/")
    disk_io = psutil.disk_io_counters()

    # Network
    net = psutil.net_io_counters()

    # Boot time
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"

    # Temperature (macOS)
    temp_info = ""
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
            ["sudo", "powermetrics", "--samplers", "smc", "-n", "1", "-i", "100"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split("\n"):
                if "CPU die temperature" in line:
                    temp_info = f"\n  Temperature: {line.strip()}"
                    break
        except Exception:
            pass

    report = f"""SYSTEM STATUS REPORT
{'=' * 50}
  Host: {platform.node()}
  OS: {platform.system()} {platform.release()} ({platform.machine()})
  Python: {platform.python_version()}
  Uptime: {uptime_str}
  Boot time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}

CPU:
  Usage: {cpu_percent}%
  Cores: {cpu_count_physical} physical / {cpu_count} logical
  Frequency: {cpu_freq.current:.0f} MHz{temp_info}

MEMORY:
  Total: {mem.total / (1024**3):.1f} GB
  Used: {mem.used / (1024**3):.1f} GB ({mem.percent}%)
  Available: {mem.available / (1024**3):.1f} GB
  Swap: {swap.used / (1024**3):.1f} / {swap.total / (1024**3):.1f} GB

DISK:
  Total: {disk.total / (1024**3):.1f} GB
  Used: {disk.used / (1024**3):.1f} GB ({disk.percent}%)
  Free: {disk.free / (1024**3):.1f} GB

NETWORK:
  Bytes sent: {net.bytes_sent / (1024**2):.1f} MB
  Bytes received: {net.bytes_recv / (1024**2):.1f} MB
  Packets sent: {net.packets_sent:,}
  Packets received: {net.packets_recv:,}"""

    return report


def get_top_processes(limit: int = 10, sort_by: str = "cpu") -> str:
    """Get top processes by CPU or memory usage."""
    if not HAS_PSUTIL:
        return "Install psutil: pip install psutil"

    procs = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "username"]):
        try:
            info = proc.info
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if sort_by == "memory":
        procs.sort(key=lambda p: p.get("memory_percent", 0), reverse=True)
        sort_label = "MEMORY"
    else:
        procs.sort(key=lambda p: p.get("cpu_percent", 0), reverse=True)
        sort_label = "CPU"

    procs = procs[:limit]

    report = f"TOP PROCESSES BY {sort_label.upper()}\n{'=' * 60}\n"
    report += f"{'PID':>8}  {'CPU%':>6}  {'MEM%':>6}  {'Name':<30}  User\n"
    report += "-" * 60 + "\n"

    for p in procs:
        pid = p.get("pid", "?")
        cpu = p.get("cpu_percent", 0)
        mem = p.get("memory_percent", 0)
        name = (p.get("name", "?") or "?")[:30]
        user = (p.get("username", "?") or "?")[:20]
        report += f"{pid:>8}  {cpu:>5.1f}%  {mem:>5.1f}%  {name:<30}  {user}\n"

    return report


def kill_process(text: str) -> str:
    """Kill a process by name or PID."""
    if not HAS_PSUTIL:
        return "Install psutil: pip install psutil"

    # Extract process name or PID
    for prefix in ["kill process", "kill", "end process", "stop process", "terminate"]:
        if prefix in text.lower():
            target = text.lower().split(prefix, 1)[-1].strip()
            break
    else:
        return "Which process would you like me to kill? Example: kill process Safari"

    if not target:
        return "Which process would you like me to kill?"

    killed = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            info = proc.info
            name = info.get("name", "")
            pid = info.get("pid", 0)

            # Match by name or PID
            if target == str(pid) or target.lower() in name.lower():
                proc.terminate()
                killed.append(f"{name} (PID: {pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed:
        return f"Terminated: {', '.join(killed)}"
    return f"I couldn't find a process matching '{target}', sir."


def get_network_connections() -> str:
    """List active network connections."""
    if not HAS_PSUTIL:
        return "Install psutil: pip install psutil"

    try:
        connections = psutil.net_connections(kind="inet")
        if not connections:
            return "No active network connections, sir."

        report = "ACTIVE NETWORK CONNECTIONS\n"
        report += f"{'Proto':<6} {'Local Address':<25} {'Remote Address':<25} {'Status':<12} {'PID':>6}\n"
        report += "-" * 80 + "\n"

        for conn in connections[:30]:  # Limit to 30
            proto = "TCP" if conn.type == 1 else "UDP"
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "*"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*"
            status = conn.status or "N/A"
            pid = conn.pid or "-"
            report += f"{proto:<6} {laddr:<25} {raddr:<25} {status:<12} {pid:>6}\n"

        return report
    except Exception as e:
        return f"Error reading connections: {e}"


def get_battery_detail() -> str:
    """Detailed battery information."""
    if not HAS_PSUTIL:
        return "Install psutil: pip install psutil"

    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "No battery detected (desktop Mac?), sir."

        plugged = "plugged in" if battery.power_plugged else "on battery"
        secs_left = battery.secsleft

        if secs_left == psutil.POWER_TIME_UNLIMITED:
            time_left = "unlimited"
        elif secs_left == psutil.POWER_TIME_UNKNOWN:
            time_left = "unknown"
        else:
            hours = secs_left // 3600
            minutes = (secs_left % 3600) // 60
            time_left = f"{hours}h {minutes}m"

        return (
            f"Battery: {battery.percent}% ({plugged})\n"
            f"  Time remaining: {time_left}"
        )
    except Exception as e:
        return f"Error reading battery: {e}"


def get_top_processes_wrapper(text: str) -> str:
    """Wrapper for command routing."""
    sort_by = "cpu"
    if "memory" in text or "mem" in text:
        sort_by = "memory"
    return get_top_processes(limit=10, sort_by=sort_by)


def monitor_alerts() -> str | None:
    """Check for system alerts (high CPU, low disk, low battery). Returns alert message or None."""
    if not HAS_PSUTIL:
        return None

    alerts = []

    # High CPU
    cpu = psutil.cpu_percent(interval=0.5)
    if cpu > 90:
        alerts.append(f"CPU usage is critically high at {cpu:.0f}%")

    # Low memory
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        alerts.append(f"Memory usage is at {mem.percent:.0f}%")

    # Low disk
    disk = psutil.disk_usage("/")
    if disk.percent > 90:
        alerts.append(f"Disk usage is at {disk.percent:.0f}%")

    # Low battery
    try:
        battery = psutil.sensors_battery()
        if battery and not battery.power_plugged and battery.percent < 20:
            alerts.append(f"Battery is low at {battery.percent}%")
    except Exception:
        pass

    if alerts:
        return "System alerts:\n  - " + "\n  - ".join(alerts)
    return None

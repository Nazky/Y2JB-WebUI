import psutil
import platform
import subprocess
import os
import sys
import datetime

def get_system_stats():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used = round(mem.used / (1024 ** 3), 2)
        ram_total = round(mem.total / (1024 ** 3), 2)
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = str(datetime.datetime.now() - boot_time).split('.')[0]
        return {
            "cpu": cpu_percent,
            "ram": {
                "percent": ram_percent,
                "used": ram_used,
                "total": ram_total
            },
            "disk": disk_percent,
            "uptime": uptime,
            "os": f"{platform.system()} {platform.release()}"
        }
    except Exception as e:
        return {"error": str(e)}

def power_control(action):
    system_platform = platform.system().lower()
    try:
        if action == "reboot":
            if "windows" in system_platform:
                os.system("shutdown /r /t 0")
            else:
                os.system("sudo reboot" if not is_docker() else "kill 1")
        elif action == "shutdown":
            if "windows" in system_platform:
                os.system("shutdown /s /t 0")
            else:
                os.system("sudo shutdown now" if not is_docker() else "kill 1")
        return True, f"Initiating {action}..."
    except Exception as e:
        return False, str(e)

def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )
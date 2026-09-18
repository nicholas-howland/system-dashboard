import datetime
import socket
import time
from flask import Flask, jsonify, render_template
from flask_basicauth import BasicAuth
import psutil

app = Flask(__name__)

app.config["BASIC_AUTH_USERNAME"] = "admin"
app.config["BASIC_AUTH_PASSWORD"] = "CHANGEME"
app.config["BASIC_AUTH_FORCE"] = True

basic_auth = BasicAuth(app)

BOOT_TIME = psutil.boot_time()
last_net_io = psutil.net_io_counters()
last_time = time.time()

def get_top_processes(limit=10):
    processes = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            pinfo = proc.info
            processes.append({
                "pid": pinfo["pid"],
                "name": pinfo["name"] or "N/A",
                "cpu_percent": round(pinfo["cpu_percent"] or 0.0, 1),
                "memory_percent": round(pinfo["memory_percent"] or 0.0, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort processes by CPU usage descending
    processes = sorted(processes, key=lambda p: p["cpu_percent"], reverse=True)
    return processes[:limit]


def get_network_connections():
    connections = []
    # Map socket type constants to readable strings
    socket_types = {socket.SOCK_STREAM: "TCP", socket.SOCK_DGRAM: "UDP"}

    try:
        net_conns = psutil.net_connections(kind="inet")
        for conn in net_conns:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "*:*"
            proto = socket_types.get(conn.type, "RAW")
            
            connections.append({
                "protocol": proto,
                "local_address": laddr,
                "foreign_address": raddr,
                "status": conn.status if conn.status else "N/A"
            })
    except (psutil.AccessDenied, PermissionError):
        pass

    return connections


def get_system_metrics():
    global last_net_io, last_time
    uptime_seconds = time.time() - BOOT_TIME
    uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))


    # Calculate network speed (MB/s)
    current_net_io = psutil.net_io_counters()
    current_time = time.time()

    time_delta = current_time - last_time
    # Prevent division by zero if updates happen instantly
    if time_delta <= 0:
        time_delta = 1

    bytes_sent_per_sec = (current_net_io.bytes_sent - last_net_io.bytes_sent) / time_delta
    bytes_recv_per_sec = (current_net_io.bytes_recv - last_net_io.bytes_recv) / time_delta

    # Convert to Megabytes per second (MB/s)
    mb_sent = round(bytes_sent_per_sec / (1024 *1024), 2)
    mb_recv = round(bytes_recv_per_sec / (1024 *1024), 2)

    # Update global states for the next interval
    last_net_io = current_net_io
    last_time = current_time


    return {
        "cpu_usage": psutil.cpu_percent(interval=None),
        "cpu_count": psutil.cpu_count(),
        "ram_usage": psutil.virtual_memory().percent,
        "ram_total": round(psutil.virtual_memory().total / (1024**3), 2),
        "ram_used": round(psutil.virtual_memory().used / (1024**3), 2),
        "disk_usage": psutil.disk_usage("/").percent,
        "disk_total": round(psutil.disk_usage("/").total / (1024**3), 2),
        "disk_used": round(psutil.disk_usage("/").used / (1024**3), 2),
        "uptime": uptime_string,
        "processes": get_top_processes(10),
        "connections": get_network_connections(),
        "net_sent": mb_sent,
        "net_recv": mb_recv,
    }


@app.route("/")
def index():
    metrics = get_system_metrics()
    return render_template("index.html", metrics=metrics)
# uncomment if you have downloaded chartjs locally, not reccomended generally
# wget https://cdn.jsdelivr.net/npm/chart.js
#@app.route("/chart.js")
#def chartjs():
#    return render_template("chart.js")


@app.route("/api/metrics")
def api_metrics():
    return jsonify(get_system_metrics())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False,ssl_context=('system-dashboard.crt', 'system-dashboard.key'))

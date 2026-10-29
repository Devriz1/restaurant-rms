import os
import sys
import time
import signal
import socket
import threading
import subprocess
import asyncio
from dotenv import load_dotenv

# Force UTF-8 console output on Windows so Unicode log characters (✓ ⚠ ✗) don't crash
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Try importing websockets for client-based auto-shutdown
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

HOST = "0.0.0.0"
DEFAULT_PORT = 8000
WS_PORT_START = 8001  # Port reserved for Heartbeat monitoring

load_dotenv(os.path.join(PROJECT_DIR, ".env"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

django_process = None
pwa_process = None
active_clients = set()
last_heartbeat_time = time.time()
shutdown_event = threading.Event()

# ==========================================================
# LOGGING
# ==========================================================

def info(message):
    print(f"[RMS] {message}", flush=True)

def success(message):
    print(f"[RMS] ✓ {message}", flush=True)

def warning(message):
    print(f"[RMS] ⚠ {message}", flush=True)

def error(message):
    print(f"[RMS] ✗ {message}", flush=True)

# ==========================================================
# NETWORK & PORT HELPERS
# ==========================================================

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip

def find_available_port(start_port=8000, max_attempts=50):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.bind((HOST, port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Could not find an open port in range {start_port}-{start_port + max_attempts}")

LOCAL_IP = get_local_ip()
PORT = find_available_port(DEFAULT_PORT)
WS_PORT = find_available_port(WS_PORT_START, max_attempts=100)
LAN_URL = f"http://{LOCAL_IP}:{PORT}"
LOCAL_FALLBACK_URL = f"http://127.0.0.1:{PORT}"

os.environ["ALLOWED_HOSTS"] = f"127.0.0.1,localhost,{LOCAL_IP},*"
os.environ["WS_PORT"] = str(WS_PORT)

# ==========================================================
# WEBSOCKET HEARTBEAT MONITOR
# ==========================================================

async def ws_handler(websocket):
    global last_heartbeat_time
    client_id = id(websocket)
    active_clients.add(client_id)
    last_heartbeat_time = time.time()
    info(f"Browser client connected ({len(active_clients)} active).")

    try:
        async for message in websocket:
            if message == "ping":
                last_heartbeat_time = time.time()
                await websocket.send("pong")
    except Exception:
        pass
    finally:
        active_clients.remove(client_id)
        info(f"Browser client disconnected ({len(active_clients)} active remaining).")

async def start_ws_server():
    async with websockets.serve(ws_handler, HOST, WS_PORT):
        await asyncio.Future()  # Run forever

def run_ws_loop():
    try:
        asyncio.run(start_ws_server())
    except OSError as exc:
        error(f"WebSocket heartbeat server failed to start on port {WS_PORT}: {exc}")
    except Exception as exc:
        error(f"WebSocket heartbeat server error: {exc}")

def monitor_heartbeat(timeout_seconds=5):
    """Monitors heartbeat pings; triggers shutdown if all clients close."""
    global last_heartbeat_time
    
    # Wait for the first client to connect (grace period: 15s)
    startup_grace = time.time()
    while len(active_clients) == 0:
        if time.time() - startup_grace > 15:
            warning("No browser client connected within 15 seconds.")
            return
        time.sleep(0.5)

    info("Client connection verified. Active monitoring engaged.")

    while not shutdown_event.is_set():
        if len(active_clients) == 0 and (time.time() - last_heartbeat_time) > timeout_seconds:
            info("All browser windows closed. Shutting down server automatically...")
            shutdown_event.set()
            break
        time.sleep(1)

# ==========================================================
# SERVER CONTROLS
# ==========================================================

def is_port_open(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()

def wait_for_port(host, port, timeout=15):
    """Poll until a port accepts connections or timeout is reached."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_open(host, port):
            return True
        time.sleep(0.5)
    return False

def start_django():
    global django_process
    python_executable = sys.executable

    use_waitress = False
    try:
        import waitress  # noqa: F401
        use_waitress = True
    except ImportError:
        use_waitress = False

    if use_waitress:
        info(f"Starting Waitress WSGI Server on LAN ({HOST}:{PORT})...")
        command = [
            python_executable,
            "-m",
            "waitress",
            f"--host={HOST}",
            f"--port={PORT}",
            "--threads=12",
            "config.wsgi:application",
        ]
    else:
        info(f"Starting Django server on LAN ({HOST}:{PORT})...")
        manage_py = os.path.join(PROJECT_DIR, "manage.py")
        command = [
            python_executable,
            manage_py,
            "runserver",
            f"{HOST}:{PORT}",
            "--noreload",
        ]

    try:
        django_process = subprocess.Popen(
            command,
            cwd=PROJECT_DIR,
            creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0),
        )
        return True
    except Exception as exc:
        error(f"Could not start backend server: {exc}")
        return False

def launch_pwa_window():
    global pwa_process
    target_url = LAN_URL
    info(f"Launching desktop PWA target: {target_url}")

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    browser_bin = chrome_path if os.path.exists(chrome_path) else edge_path

    if os.path.exists(browser_bin):
        user_data_dir = os.path.join(PROJECT_DIR, ".pwa_profile")
        pwa_process = subprocess.Popen([
            browser_bin,
            f"--app={target_url}",
            f"--user-data-dir={user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check"
        ])
        success("Desktop PWA window opened.")
        return True
    else:
        import webbrowser
        webbrowser.open(target_url)
        return False

def cleanup():
    global django_process, pwa_process
    info("Shutting down RMS local network server...")

    if pwa_process and pwa_process.poll() is None:
        try:
            pwa_process.terminate()
        except Exception:
            pass

    if django_process and django_process.poll() is None:
        try:
            django_process.terminate()
            django_process.wait(timeout=3)
        except Exception:
            django_process.kill()

    success("RMS local backend stopped cleanly.")

# ==========================================================
# MAIN EXECUTION
# ==========================================================

def main():
    info("==========================================")
    info("     RESTAURANT RMS LOCAL NETWORK SERVER  ")
    info("==========================================")

    if not HAS_WEBSOCKETS:
        warning("`websockets` package not installed ('pip install websockets').")
        warning("Install it to enable automatic browser closure detection.")

    if not start_django():
        error("Backend server failed to start.")
        return

    # Wait for the Django server to be ready (detects app load failures)
    info("Waiting for backend to be ready...")
    if not wait_for_port("127.0.0.1", PORT, timeout=15):
        error(f"Backend server did not become ready on port {PORT} within 15 seconds.")
        error("Check that all dependencies (e.g. whitenoise) are installed.")
        cleanup()
        return
    success("Backend server is ready.")

    # Start WebSocket Server in background thread
    if HAS_WEBSOCKETS:
        ws_thread = threading.Thread(target=run_ws_loop, daemon=True)
        ws_thread.start()

    print()
    info("------------------------------------------")
    success(f"Local App Endpoint: {LOCAL_FALLBACK_URL}")
    success(f"LAN Access Endpoint: {LAN_URL}")
    info("------------------------------------------")
    print()

    # Launch the browser/PWA window first so it has time to connect
    # to the WebSocket heartbeat server before monitoring begins.
    launch_pwa_window()

    if HAS_WEBSOCKETS:
        monitor_thread = threading.Thread(target=monitor_heartbeat, daemon=True)
        monitor_thread.start()

    try:
        while not shutdown_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

def handle_exit(signum, frame):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    main()
import os
import sys
import time
import signal
import socket
import subprocess
from dotenv import load_dotenv

try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None


# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

HOST = "0.0.0.0"
PORT = 8000

LOCAL_URL = f"http://127.0.0.1:{PORT}"

# Load .env configuration
load_dotenv(os.path.join(PROJECT_DIR, ".env"))
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

django_process = None
pwa_process = None
ngrok_url = None


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
# CHECK PORT & SERVER STATUS
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


def wait_for_django(timeout=30):
    info("Waiting for Django to initialize...")
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open("127.0.0.1", PORT):
            success(f"Django is running on port {PORT}")
            return True
        time.sleep(0.5)

    error("Django did not start within the timeout.")
    return False


# ==========================================================
# START DJANGO
# ==========================================================

def start_django():
    global django_process

    info("Starting Django server...")

    python_executable = sys.executable
    manage_py = os.path.join(PROJECT_DIR, "manage.py")

    if not os.path.exists(manage_py):
        error("manage.py was not found.")
        return False

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
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            ),
        )
        return wait_for_django()

    except Exception as exc:
        error(f"Could not start Django: {exc}")
        return False


# ==========================================================
# START NGROK
# ==========================================================

def start_ngrok():
    global ngrok_url

    if not NGROK_AUTHTOKEN or not ngrok:
        warning("NGROK_AUTHTOKEN missing or pyngrok not installed. Running local mode only.")
        return False

    # Force kill lingering orphan ngrok processes to prevent ERR_NGROK_334
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/IM", "ngrok.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    info("Starting ngrok tunnel...")

    try:
        ngrok.set_auth_token(NGROK_AUTHTOKEN)
        tunnel = ngrok.connect(PORT, "http")
        ngrok_url = tunnel.public_url.replace("http://", "https://")

        success(f"Public HTTPS URL: {ngrok_url}")
        return True

    except Exception as exc:
        warning(f"Could not start ngrok: {exc}")
        warning("RMS will continue locally.")
        return False


# ==========================================================
# OPEN INSTALLED PWA DESKTOP APP
# ==========================================================

def launch_pwa_window():
    global pwa_process

    info("Launching Installed Desktop PWA...")

    # Path explicitly targeting user's Chrome Apps directory
    app_data = os.environ.get("APPDATA", r"C:\Users\risal\AppData\Roaming")
    chrome_apps_dir = os.path.join(app_data, r"Microsoft\Windows\Start Menu\Programs\Chrome Apps")

    # Scans directory for installed RMS shortcut file (.lnk)
    pwa_shortcut = None
    if os.path.exists(chrome_apps_dir):
        for file in os.listdir(chrome_apps_dir):
            if file.endswith(".lnk") and "restaurant" in file.lower():
                pwa_shortcut = os.path.join(chrome_apps_dir, file)
                break
        
        # Default name check if scan finds nothing specific
        if not pwa_shortcut:
            default_lnk = os.path.join(chrome_apps_dir, "Restaurant RMS.lnk")
            if os.path.exists(default_lnk):
                pwa_shortcut = default_lnk

    if pwa_shortcut and os.path.exists(pwa_shortcut):
        info(f"Opening installed PWA shortcut: {os.path.basename(pwa_shortcut)}")
        pwa_process = subprocess.Popen(["cmd", "/c", "start", "", pwa_shortcut], shell=True)
        success("Installed Desktop PWA active.")
    else:
        info("Installed shortcut not found in Chrome Apps. Launching via standalone App mode...")
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        
        browser_bin = chrome_path if os.path.exists(chrome_path) else edge_path
        
        if os.path.exists(browser_bin):
            user_data_dir = os.path.join(PROJECT_DIR, ".pwa_profile")
            pwa_process = subprocess.Popen([
                browser_bin,
                f"--app={LOCAL_URL}",
                f"--user-data-dir={user_data_dir}",
                "--no-first-run",
                "--no-default-browser-check"
            ])
            success("Desktop PWA window opened.")
        else:
            warning("Browser executable not found. Opening system default browser...")
            import webbrowser
            webbrowser.open(LOCAL_URL)


# ==========================================================
# CLEANUP & TERMINATION
# ==========================================================

def cleanup():
    global django_process, pwa_process

    info("Shutting down RMS server and tunnels...")

    # Force kill lingering ngrok executable on Windows
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/IM", "ngrok.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Close PWA process window if active
    if pwa_process and pwa_process.poll() is None:
        try:
            pwa_process.terminate()
        except Exception:
            pass

    # Stop pyngrok session
    if ngrok:
        try:
            ngrok.kill()
        except Exception:
            pass

    # Stop Django process
    if django_process and django_process.poll() is None:
        try:
            django_process.terminate()
            django_process.wait(timeout=3)
        except Exception:
            django_process.kill()

    success("RMS, ngrok, and backend services stopped cleanly.")


# ==========================================================
# MAIN EXECUTION
# ==========================================================

def main():
    info("==========================================")
    info("         RESTAURANT RMS SERVER            ")
    info("==========================================")

    if not start_django():
        error("Django server failed to start.")
        return

    start_ngrok()

    print()
    info("------------------------------------------")
    success(f"Local Access:   {LOCAL_URL}")
    if ngrok_url:
        success(f"Remote Access:  {ngrok_url}")
        info("Customer phones/tablets can use the remote HTTPS URL.")
    info("------------------------------------------")
    print()

    launch_pwa_window()

    info("Server is running. Press CTRL+C in this console window to exit everything.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


# ==========================================================
# ENTRY POINT & SIGNAL HANDLERS
# ==========================================================

def handle_exit(signum, frame):
    cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)

if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, handle_exit)


if __name__ == "__main__":
    main()
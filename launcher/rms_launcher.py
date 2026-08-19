import socket
import subprocess
import sys
import time
import webview
from pathlib import Path



# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MANAGE_PY = BASE_DIR / "manage.py"

VENV_PYTHON = (
    BASE_DIR
    / ".venv"
    / "Scripts"
    / "python.exe"
)

DEFAULT_PORT = 8000
MAX_PORT = 8999


# ==========================================================
# CONSOLE COLORS
# ==========================================================

class Colors:

    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"


# ==========================================================
# CONSOLE HELPERS
# ==========================================================

def info(message):

    print(
        f"{Colors.CYAN}[RMS]{Colors.RESET} {message}"
    )


def success(message):

    print(
        f"{Colors.GREEN}[OK]{Colors.RESET} {message}"
    )


def warning(message):

    print(
        f"{Colors.YELLOW}[WARNING]{Colors.RESET} {message}"
    )


def error(message):

    print(
        f"{Colors.RED}[ERROR]{Colors.RESET} {message}"
    )


# ==========================================================
# GET LOCAL IPv4
# ==========================================================

def get_local_ip():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
    )

    try:

        # This does not actually send data.
        # It allows Windows to determine
        # the active network interface.

        sock.connect(
            ("8.8.8.8", 80)
        )

        return sock.getsockname()[0]

    except Exception:

        return "127.0.0.1"

    finally:

        sock.close()


# ==========================================================
# CHECK PORT
# ==========================================================

def is_port_available(port):

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    try:

        sock.bind(
            ("0.0.0.0", port)
        )

        return True

    except OSError:

        return False

    finally:

        sock.close()


# ==========================================================
# FIND AVAILABLE PORT
# ==========================================================

def find_available_port():

    for port in range(
        DEFAULT_PORT,
        MAX_PORT + 1,
    ):

        if is_port_available(port):

            return port

    return None


# ==========================================================
# RESOLVE PYTHON
# ==========================================================

def resolve_python_executable():

    if VENV_PYTHON.exists():

        return str(
            VENV_PYTHON
        )

    warning(
        "Virtual environment not found."
    )

    warning(
        "Using current Python executable."
    )

    return sys.executable


# ==========================================================
# CHECK PROJECT
# ==========================================================

def check_project():

    if not MANAGE_PY.exists():

        error(
            f"manage.py not found:\n{MANAGE_PY}"
        )

        return False

    return True


# ==========================================================
# RUN DATABASE MIGRATIONS
# ==========================================================

def run_migrations(
    python_executable,
):

    info(
        "Checking database migrations..."
    )

    command = [

        python_executable,

        str(MANAGE_PY),

        "migrate",

        "--noinput",

    ]

    try:

        result = subprocess.run(
            command,
            cwd=BASE_DIR,
        )

    except Exception as exc:

        error(
            f"Could not run migrations: {exc}"
        )

        return False

    if result.returncode != 0:

        error(
            "Database migration failed."
        )

        return False

    success(
        "Database is ready."
    )

    return True


# ==========================================================
# START DJANGO
# ==========================================================

def start_django(
    python_executable,
    port,
):

    command = [

        python_executable,

        str(MANAGE_PY),

        "runserver",

        f"0.0.0.0:{port}",

        "--noreload",

    ]

    info(
        "Starting Django HTTP server..."
    )

    try:

        process = subprocess.Popen(
            command,
            cwd=BASE_DIR,
        )

        return process

    except Exception as exc:

        error(
            f"Could not start Django: {exc}"
        )

        return None


# ==========================================================
# WAIT FOR DJANGO SERVER
# ==========================================================

def wait_for_server(
    process,
    host,
    port,
    timeout=20,
):

    info(
        "Waiting for RMS server..."
    )

    start_time = time.time()

    while (
        time.time() - start_time
        < timeout
    ):

        # Check whether Django has crashed.

        if process.poll() is not None:

            return False

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        sock.settimeout(0.5)

        try:

            result = sock.connect_ex(
                (host, port)
            )

            if result == 0:

                return True

        except Exception:

            pass

        finally:

            sock.close()

        time.sleep(0.5)

    return False


# ==========================================================
# OPEN RMS IN PYWEBVIEW
# ==========================================================

def open_rms(url):

    info(
        "Starting Restaurant RMS desktop window..."
    )

    try:

        window = webview.create_window(
            "Restaurant RMS",
            url,
            width=1400,
            height=900,
            min_size=(1000, 700),
            resizable=True,
            text_select=True,
        )

        webview.start()

        return True

    except Exception as exc:

        error(
            f"Could not start RMS desktop window: {exc}"
        )

        return False

# ==========================================================
# STOP DJANGO
# ==========================================================

def stop_django(process):

    if process is None:

        return

    if process.poll() is not None:

        return

    warning(
        "Stopping RMS server..."
    )

    try:

        process.terminate()

        process.wait(
            timeout=5
        )

    except subprocess.TimeoutExpired:

        warning(
            "Django did not stop normally."
        )

        try:

            process.kill()

        except Exception:

            pass

    except Exception:

        try:

            process.kill()

        except Exception:

            pass


# ==========================================================
# MAIN
# ==========================================================

def main():

    print()

    print(
        "=" * 65
    )

    print(
        "                 RESTAURANT RMS"
    )

    print(
        "                    Launcher"
    )

    print(
        "=" * 65
    )

    print()


    # ======================================================
    # CHECK PROJECT
    # ======================================================

    info(
        "Checking RMS project..."
    )

    if not check_project():

        input(
            "\nPress Enter to exit..."
        )

        sys.exit(1)

    success(
        "RMS project found."
    )


    # ======================================================
    # PYTHON
    # ======================================================

    python_executable = (
        resolve_python_executable()
    )

    success(
        f"Python: {python_executable}"
    )


    # ======================================================
    # DETECT LOCAL IPv4
    # ======================================================

    info(
        "Detecting local network..."
    )

    local_ip = get_local_ip()

    success(
        f"Local IPv4: {local_ip}"
    )


    # ======================================================
    # FIND AVAILABLE PORT
    # ======================================================

    info(
        "Finding available port..."
    )

    port = find_available_port()

    if port is None:

        error(
            f"No available port between "
            f"{DEFAULT_PORT} and {MAX_PORT}."
        )

        input(
            "\nPress Enter to exit..."
        )

        sys.exit(1)

    success(
        f"Port selected: {port}"
    )


    # ======================================================
    # URLS
    # ======================================================

    local_url = (
        f"http://127.0.0.1:{port}"
    )

    network_url = (
        f"http://{local_ip}:{port}"
    )


    # ======================================================
    # RUN MIGRATIONS
    # ======================================================

    if not run_migrations(
        python_executable
    ):

        input(
            "\nPress Enter to exit..."
        )

        sys.exit(1)


    # ======================================================
    # START DJANGO
    # ======================================================

    process = start_django(
        python_executable,
        port,
    )

    if process is None:

        input(
            "\nPress Enter to exit..."
        )

        sys.exit(1)


    # ======================================================
    # WAIT FOR DJANGO
    # ======================================================

    server_started = wait_for_server(
        process,
        "127.0.0.1",
        port,
    )

    if not server_started:

        error(
            "Django failed to start."
        )

        stop_django(
            process
        )

        input(
            "\nPress Enter to exit..."
        )

        sys.exit(1)


    success(
        "RMS server is running."
    )


    # ======================================================
    # OPEN RMS
    # ======================================================

    open_rms(
        local_url
    )


    # ======================================================
    # DISPLAY INFORMATION
    # ======================================================

    print()

    print(
        "=" * 65
    )

    print(
        "                    RMS IS RUNNING"
    )

    print(
        "=" * 65
    )

    print()

    print(
        "Desktop / Laptop:"
    )

    print(
        f"  {local_url}"
    )

    print()

    print(
        "Same Wi-Fi devices:"
    )

    print(
        f"  {network_url}"
    )

    print()

    print(
        "Port:"
    )

    print(
        f"  {port}"
    )

    print()

    print(
        "HTTPS / ngrok:"
    )

    print(
        "  Not enabled yet"
    )

    print()

    print(
        "RMS server is running."
    )

    print(
        "Keep this launcher running while using RMS."
    )

    print()

    print(
        "Press CTRL+C to stop RMS."
    )

    print()


    # ======================================================
    # KEEP SERVER RUNNING
    # ======================================================

    try:

        process.wait()

    except KeyboardInterrupt:

        print()

        warning(
            "Stopping RMS..."
        )

        stop_django(
            process
        )

        success(
            "RMS stopped."
        )

        print()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()
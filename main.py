import atexit
import os
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GRADIO_HOST = "127.0.0.1"
GRADIO_PORT = 7860
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000

processes = []


def wait_for_port(host: str, port: int, timeout: float = 60.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            try:
                sock.connect((host, port))
                return True
            except OSError:
                time.sleep(0.4)
    return False


def start_script(script_name: str) -> subprocess.Popen:
    script_path = ROOT / script_name
    if not script_path.exists():
        raise FileNotFoundError(f"Missing file: {script_path}")

    creation_flags = 0
    preexec_fn = None

    if os.name == "nt":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        preexec_fn = os.setsid

    proc = subprocess.Popen(
        [sys.executable, str(script_path)],
        cwd=str(ROOT),
        creationflags=creation_flags,
        preexec_fn=preexec_fn,
    )
    processes.append(proc)
    return proc


def stop_all_processes() -> None:
    for proc in reversed(processes):
        if proc.poll() is not None:
            continue

        try:
            if os.name == "nt":
                proc.send_signal(signal.CTRL_BREAK_EVENT)
                proc.wait(timeout=3)
            else:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=3)
        except Exception:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                proc.kill()


def main() -> None:
    atexit.register(stop_all_processes)

    print("[1/3] Starting Gradio app...")
    start_script("gradio_app.py")

    if not wait_for_port(GRADIO_HOST, GRADIO_PORT, timeout=90):
        raise RuntimeError("Gradio did not start on 127.0.0.1:7860 in time.")
    print("Gradio is running at http://127.0.0.1:7860")

    print("[2/3] Starting Flask app...")
    start_script("flask_app.py")

    if not wait_for_port(FLASK_HOST, FLASK_PORT, timeout=45):
        raise RuntimeError("Flask did not start on 127.0.0.1:5000 in time.")
    print("Flask is running at http://127.0.0.1:5000")

    print("[3/3] Opening browser...")
    webbrowser.open("http://127.0.0.1:5000", new=2)

    print("Both apps are running. Press Ctrl+C here to stop both.")
    try:
        while True:
            if any(proc.poll() is not None for proc in processes):
                raise RuntimeError("One of the app processes exited unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping apps...")


if __name__ == "__main__":
    main()

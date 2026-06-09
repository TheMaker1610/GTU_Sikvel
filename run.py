"""
Точка запуска всей системы.
Поддерживает macOS, Windows и Linux.
"""

import sys
import os
import time
import socket
import subprocess

SERVER_HOSTS = ("127.0.0.1", "localhost")
SERVER_PORT = 8000
WAIT_ATTEMPTS = 120
WAIT_INTERVAL = 0.5


def _port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def wait_for_server(process) -> bool:
    print("Ожидание запуска сервера", end="", flush=True)
    for _ in range(WAIT_ATTEMPTS):
        time.sleep(WAIT_INTERVAL)
        print(".", end="", flush=True)
        if process.poll() is not None:
            print("\nОшибка: сервер завершился неожиданно.")
            return False
        if any(_port_open(host, SERVER_PORT) for host in SERVER_HOSTS):
            print(" готово")
            return True
    print(" таймаут")
    return False


def start_server() -> subprocess.Popen:
    env = os.environ.copy()

    if sys.platform == "darwin":
        env["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

    if sys.platform == "win32":
        return subprocess.Popen(
            [sys.executable, "-m", "server.main"],
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )

    return subprocess.Popen(
        [sys.executable, "-m", "server.main"],
        env=env,
    )


def stop_server(process: subprocess.Popen):
    if sys.platform == "win32":
        import signal
        process.send_signal(signal.CTRL_BREAK_EVENT)
    else:
        process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
    print("Сервер остановлен.")


def main():
    server_process = start_server()

    if not wait_for_server(server_process):
        stop_server(server_process)
        sys.exit(1)

    from client.main import main as client_main
    client_main()

    stop_server(server_process)


if __name__ == "__main__":
    main()

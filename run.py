"""
Точка запуска всей системы.
Поддерживает macOS, Windows и Linux.
"""

import sys
import os
import time
import subprocess
import urllib.request
import urllib.error

SERVER_URL = "http://127.0.0.1:8000/docs"


def wait_for_server(process) -> bool:
    print("Ожидание запуска сервера", end="", flush=True)
    for _ in range(30):
        time.sleep(0.5)
        print(".", end="", flush=True)
        if process.poll() is not None:
            print("\nОшибка: сервер завершился неожиданно.")
            return False
        try:
            urllib.request.urlopen(SERVER_URL, timeout=1)
            print(" готово")
            return True
        except urllib.error.URLError:
            pass
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

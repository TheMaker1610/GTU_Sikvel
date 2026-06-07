"""
Точка входа клиентского приложения PyQt5.
"""

import sys
from PyQt5.QtWidgets import QApplication
from client.api_client import APIClient
from client.ui.login_dialog import LoginDialog
from client.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    api_client = APIClient()
    exit_code = 0

    while True:
        login = LoginDialog(api_client)
        if login.exec_() != login.Accepted:
            break

        window = MainWindow(api_client)
        relogin = {"flag": False}

        def _on_logout():
            relogin["flag"] = True

        window.logout_requested.connect(_on_logout)
        window.show()

        exit_code = app.exec_()

        if not relogin["flag"]:
            break

    api_client.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

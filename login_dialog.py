"""
Диалог аутентификации пользователя.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox,
)
from PyQt5.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("Вход в систему ГТУ")
        self.setFixedSize(320, 180)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Система анализа данных ГТУ")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("логин")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Пользователь:", self.username_edit)
        form.addRow("Пароль:", self.password_edit)
        layout.addLayout(form)

        self.login_btn = QPushButton("Войти")
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)

    def _on_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль.")
            return
        ok = self.api_client.login(username, password)
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка входа", "Неверные учётные данные или сервер недоступен.")

"""
Главное окно клиентского приложения PyQt5.
Вкладки: Мониторинг, История показаний, Журнал логов.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QHeaderView, QStatusBar, QTabWidget,
    QPlainTextEdit, QComboBox, QMessageBox, QGridLayout,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor

MODE_COLORS = {
    "STOP":    "#95a5a6",
    "START":   "#f39c12",
    "IDLE":    "#3498db",
    "PARTIAL": "#2ecc71",
    "NOMINAL": "#27ae60",
}

MODE_OPTIONS = [
    ("STOP",    "Stop"),
    ("START",   "Start"),
    ("IDLE",    "Idle"),
    ("PARTIAL", "Partial load"),
    ("NOMINAL", "Nominal"),
]

SENSORS = [
    ("rpm",            "Частота вращения ротора", "об/мин"),
    ("exhaust_temp",   "Температура выхлопа",     "°C"),
    ("inlet_pressure", "Давление на входе",       "кПа"),
    ("fuel_flow",      "Расход топлива",          "кг/ч"),
    ("vibration",      "Вибрация подшипника",     "мм/с"),
    ("iga_position",   "Положение ВНА (IGA)",     "%"),
]


class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self._logging_out = False
        self.setWindowTitle("Система анализа данных ГТУ")
        self.setMinimumSize(960, 640)
        self._build_ui()
        self._start_refresh_timer()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self.tabs.addTab(self._build_monitor_tab(), "Мониторинг")
        self.tabs.addTab(self._build_history_tab(), "История показаний")
        self.tabs.addTab(self._build_logs_tab(), "Журнал логов")

        logout_btn = QPushButton("Выйти из аккаунта")
        logout_btn.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: white; "
            "border-radius: 4px; padding: 4px 12px; } "
            "QPushButton:hover { background-color: #a93226; }"
        )
        logout_btn.clicked.connect(self._on_logout)
        self.tabs.setCornerWidget(logout_btn, Qt.TopRightCorner)

    # ── Вкладка 1: Мониторинг ────────────────────────────────────────────────

    def _build_monitor_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top = QHBoxLayout()

        # Текущий режим
        mode_group = QGroupBox("Текущий режим ГТУ")
        mode_layout = QVBoxLayout(mode_group)
        self.mode_label = QLabel("—")
        self.mode_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        self.mode_label.setFont(font)
        self.mode_label.setStyleSheet("border-radius: 8px; padding: 12px;")
        mode_layout.addWidget(self.mode_label)
        top.addWidget(mode_group, 2)

        # Управление
        ctrl_group = QGroupBox("Управление")
        ctrl_layout = QVBoxLayout(ctrl_group)

        self.mode_combo = QComboBox()
        for key, label in MODE_OPTIONS:
            self.mode_combo.addItem(label, key)
        ctrl_layout.addWidget(QLabel("Переключить режим:"))
        ctrl_layout.addWidget(self.mode_combo)

        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self._on_force_mode)
        ctrl_layout.addWidget(apply_btn)

        ctrl_layout.addSpacing(10)

        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self._refresh)
        ctrl_layout.addWidget(refresh_btn)

        ctrl_layout.addStretch()
        top.addWidget(ctrl_group, 1)

        layout.addLayout(top)

        # Текущие показания датчиков
        sensors_group = QGroupBox("Текущие показания датчиков")
        grid = QGridLayout(sensors_group)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.sensor_cards: dict[str, dict] = {}
        for idx, (key, title, unit) in enumerate(SENSORS):
            card, value_label, unit_label, title_label = self._make_sensor_card(title, unit)
            self.sensor_cards[key] = {
                "card": card,
                "value": value_label,
                "unit": unit_label,
                "title": title_label,
            }
            grid.addWidget(card, idx // 3, idx % 3)
        layout.addWidget(sensors_group)

        # Аномалии
        anomaly_group = QGroupBox("Аномалии")
        anomaly_layout = QVBoxLayout(anomaly_group)
        self.anomaly_table = self._make_table(["Время", "Датчик", "Значение", "Описание"])
        anomaly_layout.addWidget(self.anomaly_table)
        layout.addWidget(anomaly_group)

        return tab

    @staticmethod
    def _make_sensor_card(title: str, unit: str):
        card = QWidget()
        card.setObjectName("sensorCard")
        card.setStyleSheet(
            "QWidget#sensorCard { background-color: #ecf0f1; border-radius: 8px; padding: 8px; }"
        )
        v = QVBoxLayout(card)
        v.setContentsMargins(10, 8, 10, 8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        title_label.setWordWrap(True)

        value_label = QLabel("—")
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("color: #2c3e50;")

        unit_label = QLabel(unit)
        unit_label.setAlignment(Qt.AlignRight)
        unit_label.setStyleSheet("color: #7f8c8d;")

        v.addWidget(title_label)
        v.addWidget(value_label)
        v.addWidget(unit_label)
        return card, value_label, unit_label, title_label

    # ── Вкладка 2: История ───────────────────────────────────────────────────

    def _build_history_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.history_table = self._make_table(
            ["Время", "Датчик", "Значение", "Режим", "Аномалия"]
        )
        layout.addWidget(self.history_table)
        return tab

    # ── Вкладка 3: Журнал логов ──────────────────────────────────────────────

    def _build_logs_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        btn_layout = QHBoxLayout()
        refresh_log_btn = QPushButton("Обновить журнал")
        refresh_log_btn.clicked.connect(self._update_logs)
        btn_layout.addWidget(refresh_log_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("Courier New", 10)
        self.log_view.setFont(font)
        layout.addWidget(self.log_view)

        return tab

    # ── Вспомогательные ──────────────────────────────────────────────────────

    @staticmethod
    def _make_table(headers: list) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        return table

    def _start_refresh_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(6000)
        self._refresh()

    def _refresh(self):
        self._update_status()
        self._update_history()
        if self.tabs.currentIndex() == 2:
            self._update_logs()

    # ── Обновление данных ─────────────────────────────────────────────────────

    def _update_status(self):
        data = self.api_client.get_status()
        if data is None:
            self.mode_label.setText("Нет связи с сервером")
            self.mode_label.setStyleSheet(
                "background-color: #e74c3c; color: white; border-radius: 8px; padding: 12px;"
            )
            self.status_bar.showMessage("Ошибка соединения с сервером")
            return

        mode = data.get("mode") or "STOP"
        label = data.get("mode_label", mode)
        color = MODE_COLORS.get(mode, "#bdc3c7")

        self.mode_label.setText(label)
        self.mode_label.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 8px; padding: 12px;"
        )

        # Синхронизировать комбобокс с текущим режимом
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == mode:
                self.mode_combo.blockSignals(True)
                self.mode_combo.setCurrentIndex(i)
                self.mode_combo.blockSignals(False)
                break

        anomalies = data.get("anomalies", [])
        self.anomaly_table.setRowCount(0)
        for item in anomalies:
            row = self.anomaly_table.rowCount()
            self.anomaly_table.insertRow(row)
            self.anomaly_table.setItem(row, 0, QTableWidgetItem(item.get("timestamp", "")))
            self.anomaly_table.setItem(row, 1, QTableWidgetItem(item.get("sensor", "")))
            self.anomaly_table.setItem(row, 2, QTableWidgetItem(str(item.get("value", ""))))
            self.anomaly_table.setItem(row, 3, QTableWidgetItem(item.get("description", "")))
            for col in range(4):
                cell = self.anomaly_table.item(row, col)
                if cell:
                    cell.setBackground(QColor("#c0392b"))
                    cell.setForeground(QColor("#ffffff"))

        self.status_bar.showMessage(f"Обновлено. Режим: {label}. Аномалий: {len(anomalies)}")

    def _update_history(self):
        records = self.api_client.get_records(limit=100)
        if records is None:
            return
        self.history_table.setRowCount(0)
        for rec in records:
            row = self.history_table.rowCount()
            self.history_table.insertRow(row)
            self.history_table.setItem(row, 0, QTableWidgetItem(rec.get("timestamp", "")))
            self.history_table.setItem(row, 1, QTableWidgetItem(rec.get("sensor", "")))
            self.history_table.setItem(row, 2, QTableWidgetItem(str(rec.get("value", ""))))
            self.history_table.setItem(row, 3, QTableWidgetItem(rec.get("mode_label", "")))
            anomaly_text = "Да" if rec.get("anomaly") else "Нет"
            cell = QTableWidgetItem(anomaly_text)
            if rec.get("anomaly"):
                cell.setBackground(QColor("#c0392b"))
                cell.setForeground(QColor("#ffffff"))
            self.history_table.setItem(row, 4, cell)

        self._update_sensor_cards(records)

    def _update_sensor_cards(self, records: list):
        latest: dict[str, dict] = {}
        for rec in records:
            name = rec.get("sensor")
            if name and name not in latest:
                latest[name] = rec

        for key, card in self.sensor_cards.items():
            rec = latest.get(key)
            if rec is None:
                card["value"].setText("—")
                card["card"].setStyleSheet(
                    "QWidget#sensorCard { background-color: #ecf0f1; border-radius: 8px; padding: 8px; }"
                )
                card["value"].setStyleSheet("color: #2c3e50;")
                card["title"].setStyleSheet("color: #2c3e50; font-weight: bold;")
                card["unit"].setStyleSheet("color: #7f8c8d;")
                continue

            value = rec.get("value")
            card["value"].setText(f"{value:.2f}" if isinstance(value, (int, float)) else str(value))

            if rec.get("anomaly"):
                card["card"].setStyleSheet(
                    "QWidget#sensorCard { background-color: #c0392b; border-radius: 8px; padding: 8px; }"
                )
                card["value"].setStyleSheet("color: #ffffff;")
                card["title"].setStyleSheet("color: #ffffff; font-weight: bold;")
                card["unit"].setStyleSheet("color: #f5b7b1;")
            else:
                card["card"].setStyleSheet(
                    "QWidget#sensorCard { background-color: #ecf0f1; border-radius: 8px; padding: 8px; }"
                )
                card["value"].setStyleSheet("color: #2c3e50;")
                card["title"].setStyleSheet("color: #2c3e50; font-weight: bold;")
                card["unit"].setStyleSheet("color: #7f8c8d;")

    def _update_logs(self):
        lines = self.api_client.get_logs(lines=200)
        if lines is None:
            return
        self.log_view.setPlainText("\n".join(lines))
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )

    def _on_force_mode(self):
        mode_key = self.mode_combo.currentData()
        ok = self.api_client.force_mode(mode_key)
        if ok:
            label = self.mode_combo.currentText()
            self.status_bar.showMessage(f"Режим переключён: {label}")
            self._refresh()
        else:
            self.status_bar.showMessage("Ошибка: не удалось переключить режим (нужны права admin)")

    def _on_logout(self):
        reply = QMessageBox.question(
            self,
            "Выход из аккаунта",
            "Выйти из аккаунта и вернуться к окну входа?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._logging_out = True
        self.timer.stop()
        self.api_client.logout()
        self.logout_requested.emit()
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

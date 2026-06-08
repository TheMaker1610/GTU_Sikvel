"""
Загрузчик исторических данных из Приложения 1 (формат Jupyter Notebook).

Парсит строки вида:
  1779195889.6 | об/мин=1495.42 | T=174.07°C | P=108.89кПа | топливо=240.99кг/ч | вибрация=1.04мм/с | IGA=37.37%

Возвращает список словарей с ключами:
  timestamp, rpm, exhaust_temp, inlet_pressure, fuel_flow, vibration, iga_position
"""

import re
import json
from pathlib import Path
from server.logging_service.logger import get_logger

logger = get_logger(__name__)

_LINE_RE = re.compile(
    r"(?P<ts>[\d.]+)\s*\|"
    r"\s*об/мин=(?P<rpm>[\d.]+)\s*\|"
    r"\s*T=(?P<temp>[\d.]+)°C\s*\|"
    r"\s*P=(?P<pressure>[\d.]+)кПа\s*\|"
    r"\s*топливо=(?P<fuel>[\d.]+)кг/ч\s*\|"
    r"\s*вибрация=(?P<vib>[\d.]+)мм/с\s*\|"
    r"\s*IGA=(?P<iga>[\d.]+)%"
)


def parse_line(line: str) -> dict | None:
    m = _LINE_RE.search(line)
    if not m:
        return None
    return {
        "timestamp":       float(m.group("ts")),
        "rpm":             float(m.group("rpm")),
        "exhaust_temp":    float(m.group("temp")),
        "inlet_pressure":  float(m.group("pressure")),
        "fuel_flow":       float(m.group("fuel")),
        "vibration":       float(m.group("vib")),
        "iga_position":    float(m.group("iga")),
    }


def load_notebook(path: str | Path) -> list[dict]:
    """Загружает .ipynb и извлекает все строки данных датчиков."""
    path = Path(path)
    if not path.exists():
        logger.error(f"Файл не найден: {path}")
        return []

    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    records = []
    for cell in nb.get("cells", []):
        for output in cell.get("outputs", []):
            for text_line in output.get("text", []):
                rec = parse_line(text_line)
                if rec:
                    records.append(rec)

    logger.info(f"Загружено {len(records)} записей из {path.name}")
    return records


def load_text_file(path: str | Path) -> list[dict]:
    """Загружает обычный текстовый файл с данными датчиков."""
    path = Path(path)
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = parse_line(line)
            if rec:
                records.append(rec)
    logger.info(f"Загружено {len(records)} записей из {path.name}")
    return records

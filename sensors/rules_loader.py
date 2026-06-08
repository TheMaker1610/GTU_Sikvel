"""
Загрузчик правил нормальных диапазонов из Приложения 2 (CSV-файл).

Формат CSV:
  Mode,Parameter,Min_Normal,Max_Normal,Unit

Пример использования:
  from server.sensors.rules_loader import load_rules
  rules = load_rules("Приложение_2_КМ4.txt")
  print(rules["NOMINAL"]["rpm"])   # (7840.0, 8160.0)
"""

import csv
from pathlib import Path
from server.logging_service.logger import get_logger

logger = get_logger(__name__)


def load_rules(path: str | Path) -> dict[str, dict[str, tuple[float, float]]]:
    """
    Возвращает словарь:
      { режим: { параметр: (min, max) } }
    """
    path = Path(path)
    rules: dict[str, dict[str, tuple[float, float]]] = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mode = row["Mode"].strip()
            param = row["Parameter"].strip()
            lo = float(row["Min_Normal"])
            hi = float(row["Max_Normal"])
            rules.setdefault(mode, {})[param] = (lo, hi)

    logger.info(f"Загружено правил: {sum(len(v) for v in rules.values())} из {path.name}")
    return rules

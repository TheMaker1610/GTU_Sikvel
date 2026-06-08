"""
Детектор аномалий ГТУ.

Нормальные диапазоны взяты из Приложения 2 (Приложение_2_КМ4.txt).
Выход значения датчика за пределы допустимого диапазона → аномалия.
"""

from server.logging_service.logger import get_logger

logger = get_logger(__name__)

_LIMITS: dict[str, dict[str, tuple[float, float]]] = {
    "STOP": {
        "rpm":            (0,     5),
        "exhaust_temp":   (16.5,  28.5),
        "inlet_pressure": (100.2, 101.8),
        "fuel_flow":      (0,     5),
        "vibration":      (0.02,  0.18),
        "iga_position":   (0,     0.5),
    },
    "START": {
        "rpm":            (300,   2700),
        "exhaust_temp":   (58,    362),
        "inlet_pressure": (102,   118),
        "fuel_flow":      (50,    450),
        "vibration":      (0.65,  1.85),
        "iga_position":   (10,    90),
    },
    "IDLE": {
        "rpm":            (2920,  3080),
        "exhaust_temp":   (384,   416),
        "inlet_pressure": (116,   124),
        "fuel_flow":      (484,   516),
        "vibration":      (1.85,  2.25),
        "iga_position":   (18.4,  21.6),
    },
    "PARTIAL": {
        "rpm":            (4300,  6700),
        "exhaust_temp":   (420,   580),
        "inlet_pressure": (122,   138),
        "fuel_flow":      (600,   1400),
        "vibration":      (2.2,   3.8),
        "iga_position":   (26,    74),
    },
    "NOMINAL": {
        "rpm":            (7840,  8160),
        "exhaust_temp":   (634,   666),
        "inlet_pressure": (148.4, 151.6),
        "fuel_flow":      (1960,  2040),
        "vibration":      (3.85,  4.25),
        "iga_position":   (98.2,  99.8),
    },
}

_SENSOR_LABELS = {
    "rpm":            "Частота вращения ротора",
    "exhaust_temp":   "Температура выхлопных газов",
    "inlet_pressure": "Давление на входе",
    "fuel_flow":      "Расход топлива",
    "vibration":      "Вибрация подшипника",
    "iga_position":   "Положение IGA",
}


class AnomalyDetector:
    def detect(self, readings: dict, mode: str) -> list[dict]:
        anomalies = []
        limits = _LIMITS.get(mode, {})

        for sensor, (low, high) in limits.items():
            value = readings.get(sensor)
            if value is None:
                continue
            if not (low <= value <= high):
                label = _SENSOR_LABELS.get(sensor, sensor)
                anomaly = {
                    "sensor": sensor,
                    "sensor_description": label,
                    "value": value,
                    "expected_min": low,
                    "expected_max": high,
                    "description": (
                        f"{label}: значение {value} вне допустимого диапазона [{low}, {high}]"
                    ),
                }
                anomalies.append(anomaly)
                logger.warning(f"Аномалия: {anomaly['description']}")

        return anomalies

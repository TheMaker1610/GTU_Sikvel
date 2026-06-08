"""
Сервис опроса датчиков АСУТП ГТУ.

Датчики (Приложение 1):
    rpm           — частота вращения ротора, об/мин
    exhaust_temp  — температура выхлопных газов, °C
    inlet_pressure— давление на входе, кПа
    fuel_flow     — расход топлива, кг/ч
    vibration     — вибрация подшипника, мм/с
    iga_position  — положение входного направляющего аппарата (IGA), %
"""

import random
from server.logging_service.logger import get_logger

logger = get_logger(__name__)

SENSOR_NAMES = ["rpm", "exhaust_temp", "inlet_pressure", "fuel_flow", "vibration", "iga_position"]

_MODE_RANGES = {
    "STOP": {
        "rpm":            (0.0,    5.0),
        "exhaust_temp":   (16.5,   28.5),
        "inlet_pressure": (100.2,  101.8),
        "fuel_flow":      (0.0,    5.0),
        "vibration":      (0.02,   0.18),
        "iga_position":   (0.0,    0.5),
    },
    "START": {
        "rpm":            (300.0,  2700.0),
        "exhaust_temp":   (58.0,   362.0),
        "inlet_pressure": (102.0,  118.0),
        "fuel_flow":      (50.0,   450.0),
        "vibration":      (0.65,   1.85),
        "iga_position":   (10.0,   90.0),
    },
    "IDLE": {
        "rpm":            (2920.0, 3080.0),
        "exhaust_temp":   (384.0,  416.0),
        "inlet_pressure": (116.0,  124.0),
        "fuel_flow":      (484.0,  516.0),
        "vibration":      (1.85,   2.25),
        "iga_position":   (18.4,   21.6),
    },
    "PARTIAL": {
        "rpm":            (4300.0, 6700.0),
        "exhaust_temp":   (420.0,  580.0),
        "inlet_pressure": (122.0,  138.0),
        "fuel_flow":      (600.0,  1400.0),
        "vibration":      (2.2,    3.8),
        "iga_position":   (26.0,   74.0),
    },
    "NOMINAL": {
        "rpm":            (7840.0, 8160.0),
        "exhaust_temp":   (634.0,  666.0),
        "inlet_pressure": (148.4,  151.6),
        "fuel_flow":      (1960.0, 2040.0),
        "vibration":      (3.85,   4.25),
        "iga_position":   (98.2,   99.8),
    },
}

_NOMINAL_RANGES = _MODE_RANGES["NOMINAL"]


class SensorService:
    """
    Читает показания датчиков.
    В реальной системе заменяется подключением к OPC-UA / Modbus / MQTT.
    Сейчас симулирует значения для выбранного режима ГТУ
    с добавлением шума и редких выбросов.
    """

    def __init__(self, noise_level: float = 0.02, anomaly_probability: float = 0.02):
        self.noise_level = noise_level
        self.anomaly_probability = anomaly_probability

    def poll(self, mode: str = "NOMINAL") -> dict:
        ranges = _MODE_RANGES.get(mode, _NOMINAL_RANGES)
        readings: dict[str, float] = {}
        for sensor, (low, high) in ranges.items():
            midpoint = (low + high) / 2
            half_span = (high - low) / 2
            noise = half_span * 0.6 * random.uniform(-1, 1)
            value = midpoint + noise

            if random.random() < self.anomaly_probability:
                spike_base = max(abs(midpoint), 1.0)
                spike = spike_base * random.uniform(0.15, 0.30) * random.choice([-1, 1])
                value += spike

            if sensor in ("rpm", "fuel_flow") and mode == "STOP":
                value = max(0.0, value)

            readings[sensor] = round(value, 3)

        logger.debug(f"Показания датчиков ({mode}): {readings}")
        return readings

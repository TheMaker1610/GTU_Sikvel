"""
Тесты детектора аномалий ГТУ (на основе Приложения 2).
"""

import pytest
from server.analytics.anomaly_detector import AnomalyDetector


@pytest.fixture
def detector():
    return AnomalyDetector()


def _nominal() -> dict:
    return {
        "rpm": 8000, "exhaust_temp": 650, "inlet_pressure": 150,
        "fuel_flow": 2000, "vibration": 4.0, "iga_position": 99.0,
    }

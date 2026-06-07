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


def _start() -> dict:
    return {
        "rpm": 1495, "exhaust_temp": 174, "inlet_pressure": 109,
        "fuel_flow": 241, "vibration": 1.04, "iga_position": 37.4,
    }


class TestAnomalyDetector:
    def test_no_anomaly_nominal(self, detector):
        assert detector.detect(_nominal(), "NOMINAL") == []

    def test_no_anomaly_start_appendix1_values(self, detector):
        assert detector.detect(_start(), "START") == []

    def test_vibration_anomaly_nominal(self, detector):
        r = _nominal()
        r["vibration"] = 9.0
        sensors = [a["sensor"] for a in detector.detect(r, "NOMINAL")]
        assert "vibration" in sensors

    def test_rpm_below_range(self, detector):
        r = _nominal()
        r["rpm"] = 5000
        sensors = [a["sensor"] for a in detector.detect(r, "NOMINAL")]
        assert "rpm" in sensors

    def test_temperature_above_range(self, detector):
        r = _nominal()
        r["exhaust_temp"] = 800
        sensors = [a["sensor"] for a in detector.detect(r, "NOMINAL")]
        assert "exhaust_temp" in sensors

    def test_fuel_flow_anomaly_idle(self, detector):
        r = {"rpm": 3000, "exhaust_temp": 400, "inlet_pressure": 120,
             "fuel_flow": 900, "vibration": 2.0, "iga_position": 20}
        sensors = [a["sensor"] for a in detector.detect(r, "IDLE")]
        assert "fuel_flow" in sensors

    def test_anomaly_description_in_russian(self, detector):
        r = _nominal()
        r["vibration"] = 10.0
        anomalies = detector.detect(r, "NOMINAL")
        assert anomalies
        assert "Вибрация" in anomalies[0]["description"]


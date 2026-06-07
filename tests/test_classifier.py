"""
Тесты классификатора режимов ГТУ (на основе Приложения 2).
"""

import pytest
from server.analytics.classifier import ModeClassifier


@pytest.fixture
def classifier():
    return ModeClassifier()


def _r(**kwargs) -> dict:
    base = {
        "rpm": 8000, "exhaust_temp": 650, "inlet_pressure": 150,
        "fuel_flow": 2000, "vibration": 4.0, "iga_position": 99.0,
    }
    base.update(kwargs)
    return base


class TestModeClassifier:
    def test_stop(self, classifier):
        assert classifier.classify(_r(rpm=0, fuel_flow=0)) == "STOP"

    def test_start(self, classifier):
        assert classifier.classify(_r(rpm=1500, fuel_flow=250)) == "START"

    def test_idle(self, classifier):
        assert classifier.classify(_r(rpm=3000, fuel_flow=500)) == "IDLE"

    def test_partial_load(self, classifier):
        assert classifier.classify(_r(rpm=5500, fuel_flow=1000)) == "PARTIAL"

    def test_nominal(self, classifier):
        assert classifier.classify(_r(rpm=8000, fuel_flow=2000)) == "NOMINAL"

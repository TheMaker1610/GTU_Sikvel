"""
Тесты детектора аномалий ГТУ (на основе Приложения 2).
"""

import pytest
from server.analytics.anomaly_detector import AnomalyDetector


@pytest.fixture
def detector():
    return AnomalyDetector()

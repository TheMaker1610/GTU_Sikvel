"""
Тесты сервиса опроса датчиков.
"""

import pytest
from server.sensors.sensor_service import SensorService, SENSOR_NAMES


@pytest.fixture
def sensor_service():
    return SensorService(noise_level=0.01, anomaly_probability=0.0)

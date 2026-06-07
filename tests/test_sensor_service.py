"""
Тесты сервиса опроса датчиков.
"""

import pytest
from server.sensors.sensor_service import SensorService, SENSOR_NAMES


@pytest.fixture
def sensor_service():
    return SensorService(noise_level=0.01, anomaly_probability=0.0)


class TestSensorService:
    def test_poll_returns_all_sensors(self, sensor_service):
        readings = sensor_service.poll()
        for name in SENSOR_NAMES:
            assert name in readings, f"Датчик {name} отсутствует в показаниях"

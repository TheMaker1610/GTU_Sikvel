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

    def test_poll_returns_floats(self, sensor_service):
        readings = sensor_service.poll()
        for name, value in readings.items():
            assert isinstance(value, float), f"Значение {name} не является числом"

    def test_poll_values_positive(self, sensor_service):
        for _ in range(5):
            readings = sensor_service.poll()
            assert readings["rpm"] > 0
            assert readings["exhaust_temp"] > 0
            assert readings["fuel_flow"] > 0

    def test_poll_nominal_midpoints(self):
        service = SensorService(noise_level=0.0, anomaly_probability=0.0)
        readings = service.poll()
        assert readings["rpm"] == pytest.approx(8000.0, rel=0.01)
        assert readings["exhaust_temp"] == pytest.approx(650.0, rel=0.01)
        assert readings["fuel_flow"] == pytest.approx(2000.0, rel=0.01)
# reviewed

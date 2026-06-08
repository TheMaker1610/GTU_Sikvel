"""
Оркестратор — управляет циклом опроса датчиков и аналитики.
"""
import asyncio
from server.sensors.sensor_service import SensorService
from server.analytics.anomaly_detector import AnomalyDetector
from server.storage.database import SessionLocal
from server.storage.models import SensorRecord
from server.logging_service.logger import get_logger
from server.config.settings import SENSOR_POLL_INTERVAL

logger = get_logger(__name__)

DEFAULT_MODE = "STOP"


class Orchestrator:
    def __init__(self):
        self.sensor_service = SensorService()
        self.anomaly_detector = AnomalyDetector()
        self._running = False

    async def run(self):
        self._running = True
        logger.info("Оркестратор запущен.")
        while self._running:
            try:
                await self._tick()
            except Exception as exc:
                logger.error(f"Ошибка в цикле оркестратора: {exc}")
            await asyncio.sleep(SENSOR_POLL_INTERVAL)

    async def _tick(self):
        import server.api.routes as _routes
        mode = _routes._forced_mode or DEFAULT_MODE
        readings = self.sensor_service.poll(mode)
        anomalies = self.anomaly_detector.detect(readings, mode)

        self._save(readings, mode, anomalies)

        if anomalies:
            logger.warning(f"Аномалии обнаружены: {anomalies} | Режим: {mode}")
        else:
            logger.info(f"Режим: {mode} | Аномалий нет")

    def _save(self, readings: dict, mode: str, anomalies: list):
        db = SessionLocal()
        try:
            for sensor_name, value in readings.items():
                anomaly_flag = any(a["sensor"] == sensor_name for a in anomalies)
                anomaly_desc = next(
                    (a["description"] for a in anomalies if a["sensor"] == sensor_name),
                    None,
                )
                record = SensorRecord(
                    sensor_name=sensor_name,
                    value=value,
                    mode=mode,
                    anomaly=anomaly_flag,
                    anomaly_description=anomaly_desc,
                )
                db.add(record)
            db.commit()
        finally:
            db.close()

    def stop(self):
        self._running = False
        logger.info("Оркестратор остановлен.")

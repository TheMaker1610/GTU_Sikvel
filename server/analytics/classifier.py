"""
Классификатор режимов работы ГТУ.

Правила классификации (Приложение 2):
┌──────────────────┬──────────────┬──────────────────┬────────────┬────────────┬────────────┬──────────────┐
│ Режим            │ RPM (об/мин) │ exhaust_temp (°C)│ pressure   │ fuel_flow  │ vibration  │ iga_pos (%)  │
├──────────────────┼──────────────┼──────────────────┼────────────┼────────────┼────────────┼──────────────┤
│ STOP             │ 0            │ 16.5 – 28.5      │100.2–101.8 │ 0          │0.02–0.18   │ 0            │
│ START            │ 300 – 2700   │ 58 – 362         │102–118     │50–450      │0.65–1.85   │10–90         │
│ IDLE             │ 2920 – 3080  │ 384 – 416        │116–124     │484–516     │1.85–2.25   │18.4–21.6     │
│ PARTIAL          │ 4300 – 6700  │ 420 – 580        │122–138     │600–1400    │2.2–3.8     │26–74         │
│ NOMINAL          │ 7840 – 8160  │ 634 – 666        │148.4–151.6 │1960–2040   │3.85–4.25   │98.2–99.8     │
└──────────────────┴──────────────┴──────────────────┴────────────┴────────────┴────────────┴──────────────┘
"""

from server.config.settings import GTU_MODES
from server.logging_service.logger import get_logger

logger = get_logger(__name__)


def _in(value: float, lo: float, hi: float) -> bool:
    return lo <= value <= hi


class ModeClassifier:
    def classify(self, readings: dict) -> str:
        rpm = readings.get("rpm", 0)
        fuel = readings.get("fuel_flow", 0)
        temp = readings.get("exhaust_temp", 0)
        vib = readings.get("vibration", 0)
        iga = readings.get("iga_position", 0)

        if rpm <= 5 and fuel <= 5:
            mode = "STOP"
        elif _in(rpm, 300, 2700) and _in(fuel, 50, 450):
            mode = "START"
        elif _in(rpm, 2920, 3080) and _in(fuel, 484, 516):
            mode = "IDLE"
        elif _in(rpm, 4300, 6700) and _in(fuel, 600, 1400):
            mode = "PARTIAL"
        elif _in(rpm, 7840, 8160) and _in(fuel, 1960, 2040):
            mode = "NOMINAL"
        else:
            mode = "START"

        logger.debug(f"Классифицирован режим: {GTU_MODES.get(mode, mode)}")
        return mode

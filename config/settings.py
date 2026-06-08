import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gtu_data.db")

SERVER_HOST: str = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

SENSOR_POLL_INTERVAL: int = int(os.getenv("SENSOR_POLL_INTERVAL", "5"))

GTU_MODES = {
    "STOP": "Stop",
    "START": "Start",
    "IDLE": "Idle",
    "NOMINAL": "Nominal",
    "PARTIAL": "Partial load",
}

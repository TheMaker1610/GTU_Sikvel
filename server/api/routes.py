"""
REST API маршруты.
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from server.storage.database import get_db
from server.storage.models import SensorRecord, User
from server.auth.auth_service import (
    authenticate_user,
    create_access_token,
    decode_token,
    hash_password,
)
from server.logging_service.logger import get_logger
from server.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, GTU_MODES

logger = get_logger(__name__)
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен")
    username: str = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
    return current_user


@router.post("/token", summary="Получить JWT-токен")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учётные данные")
    token = create_access_token(
        {"sub": user.username, "role": user.role},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/status", summary="Текущий режим ГТУ и последние аномалии")
def gtu_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    latest = (
        db.query(SensorRecord)
        .order_by(SensorRecord.timestamp.desc())
        .limit(50)
        .all()
    )
    if not latest:
        return {"mode": None, "mode_label": "Нет данных", "anomalies": []}

    last_mode = latest[0].mode
    anomalies = [
        {
            "timestamp": r.timestamp.isoformat(),
            "sensor": r.sensor_name,
            "value": r.value,
            "description": r.anomaly_description,
        }
        for r in latest
        if r.anomaly
    ]
    return {
        "mode": last_mode,
        "mode_label": GTU_MODES.get(last_mode, last_mode),
        "anomalies": anomalies,
    }


@router.get("/records", summary="История показаний датчиков")
def get_records(
    sensor: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(SensorRecord).order_by(SensorRecord.timestamp.desc())
    if sensor:
        query = query.filter(SensorRecord.sensor_name == sensor)
    records = query.limit(limit).all()
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "sensor": r.sensor_name,
            "value": r.value,
            "mode": r.mode,
            "mode_label": GTU_MODES.get(r.mode, r.mode),
            "anomaly": r.anomaly,
            "anomaly_description": r.anomaly_description,
        }
        for r in records
    ]


_forced_mode: Optional[str] = "STOP"


@router.post("/mode/force", summary="Установить режим ГТУ (admin)")
def force_mode(
    mode: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    global _forced_mode
    if mode not in GTU_MODES:
        raise HTTPException(status_code=400, detail=f"Неизвестный режим: {mode}")
    _forced_mode = mode
    label = GTU_MODES.get(mode, mode)
    logger.info(f"Режим установлен: {label} (пользователь: {admin.username})")
    return {"message": f"Режим установлен: {label}"}


@router.get("/mode/forced", summary="Получить текущий принудительный режим")
def get_forced_mode(current_user: User = Depends(get_current_user)):
    return {"forced_mode": _forced_mode}


@router.get("/logs", summary="Последние строки лог-файла")
def get_logs(
    lines: int = 100,
    current_user: User = Depends(get_current_user),
):
    import os
    log_path = os.path.join("logs", "gtu.log")
    if not os.path.exists(log_path):
        return {"lines": []}
    with open(log_path, encoding="utf-8") as f:
        all_lines = f.readlines()
    return {"lines": [l.rstrip() for l in all_lines[-lines:]]}


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "operator"


@router.post("/users", summary="Создать пользователя (только admin)")
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    user = User(
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.commit()
    logger.info(f"Создан новый пользователь: {body.username} (роль: {body.role})")
    return {"message": f"Пользователь {body.username} создан"}

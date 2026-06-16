"""
HTTP-клиент для взаимодействия с сервером GTU Analysis API.
"""

import httpx
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import logging
from server.config.settings import SERVER_HOST, SERVER_PORT

BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}" #Конфигурация
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Базовое исключение для ошибок API."""
    pass


class AuthenticationError(APIError):
    """Ошибка аутентификации."""
    pass


class APIClient:
    def __init__(self, base_url: str = BASE_URL, timeout: float = 10.0): #Инициализация клиента
        self._token: Optional[str] = None
        self._base_url = base_url
        self._timeout = timeout
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def login(self, username: str, password: str) -> bool:
        """
        Аутентификация пользователя.
        
        Args:
            username: Имя пользователя
            password: Пароль
            
        Returns:
            bool: Успешность аутентификации
            
        Raises:
            AuthenticationError: При ошибках аутентификации
        """
        try:
            logger.info(f"Authenticating user: {username}")
            response = self._client.post(
                "/token",
                data={"username": username, "password": password},
            )
            
            if response.status_code == 200:
                self._token = response.json()["access_token"]
                logger.info("Authentication successful")
                return True
            elif response.status_code == 401:
                logger.warning("Authentication failed: invalid credentials")
                return False
            else:
                logger.error(f"Authentication failed with status {response.status_code}")
                return False
                
        except httpx.RequestError as exc:
            logger.error(f"Request error during authentication: {exc}")
            raise AuthenticationError(f"Connection error: {exc}")

    def logout(self) -> None:
        """Очистка токена аутентификации."""
        self._token = None
        logger.info("Logged out")

    def _headers(self) -> Dict[str, str]:  #Формирование заголовков
        """Формирование заголовков запроса."""
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _handle_response(self, response: httpx.Response) -> Any: #Обработка ответов
        """Обработка ответа сервера."""
        if response.status_code == 401:
            self._token = None
            raise AuthenticationError("Token expired or invalid")
        
        if response.status_code >= 400:
            error_msg = response.json().get("detail", response.text)
            raise APIError(f"API error {response.status_code}: {error_msg}")
        
        if response.status_code == 204:
            return None
            
        return response.json()

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Получение статуса сервера."""
        try:
            response = self._client.get("/status", headers=self._headers())
            return self._handle_response(response)
        except httpx.RequestError as exc:
            logger.error(f"Failed to get status: {exc}")
            return None

    def get_records(self, sensor: Optional[str] = None, limit: int = 100) -> Optional[List[Dict]]: #Получение записей 
        """
        Получение записей с фильтрацией.
        
        Args:
            sensor: Фильтр по датчику (опционально)
            limit: Максимальное количество записей
            
        Returns:
            Список записей или None при ошибке
        """
        try:
            params = {"limit": min(limit, 1000)}  # Ограничение на максимальное значение
            if sensor:
                params["sensor"] = sensor
                
            response = self._client.get("/records", headers=self._headers(), params=params)
            return self._handle_response(response)
        except httpx.RequestError as exc:
            logger.error(f"Failed to get records: {exc}")
            return None

    def force_mode(self, mode: str) -> bool: #Управление режимом
        """
        Принудительная установка режима.
        
        Args:
            mode: Режим работы
            
        Returns:
            bool: Успешность операции
        """
        valid_modes = ["normal", "auto", "manual"]
        if mode not in valid_modes:
            logger.warning(f"Invalid mode '{mode}'. Must be one of {valid_modes}")
            return False
            
        try:
            response = self._client.post(
                "/mode/force",
                params={"mode": mode},
                headers=self._headers(),
            )
            self._handle_response(response)
            return True
        except (APIError, httpx.RequestError) as exc:
            logger.error(f"Failed to force mode: {exc}")
            return False

    def get_forced_mode(self) -> Optional[str]:
        """Получение принудительного режима."""
        try:
            response = self._client.get("/mode/forced", headers=self._headers())
            data = self._handle_response(response)
            return data.get("forced_mode")
        except (APIError, httpx.RequestError) as exc:
            logger.error(f"Failed to get forced mode: {exc}")
            return None

    def get_logs(self, lines: int = 200) -> Optional[List[str]]: #Получение логов
        """
        Получение логов сервера.
        
        Args:
            lines: Количество строк лога
            
        Returns:
            Список строк лога или None при ошибке
        """
        try:
            params = {"lines": min(lines, 1000)}  # Ограничение на максимальное значение
            response = self._client.get(
                "/logs",
                params=params,
                headers=self._headers(),
            )
            data = self._handle_response(response)
            return data.get("lines", [])
        except (APIError, httpx.RequestError) as exc:
            logger.error(f"Failed to get logs: {exc}")
            return None

    @asynccontextmanager
    async def async_client(self):
        """Контекстный менеджер для асинхронного клиента."""
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            yield client

    def __enter__(self): #Контекстный менеджер
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): #Асинхронный клиент
        self.close()

    def close(self): 
        """Закрытие HTTP-клиента."""
        self._client.close()
        logger.info("Client closed") #Логирование

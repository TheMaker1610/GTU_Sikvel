"""
HTTP-клиент для взаимодействия с сервером GTU Analysis API.
"""

import httpx
from server.config.settings import SERVER_HOST, SERVER_PORT

BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"


class APIClient:
    def __init__(self):
        self._token: str | None = None
        self._client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    def login(self, username: str, password: str) -> bool:
        try:
            print(f"[APIClient] POST {BASE_URL}/token (user={username!r})")
            response = self._client.post(
                "/token",
                data={"username": username, "password": password},
            )
            print(f"[APIClient] status={response.status_code} body={response.text[:200]}")
            if response.status_code == 200:
                self._token = response.json()["access_token"]
                return True
            return False
        except httpx.RequestError as exc:
            print(f"[APIClient] RequestError: {type(exc).__name__}: {exc}")
            return False

    def logout(self) -> None:
        self._token = None

    def _headers(self) -> dict:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def get_status(self) -> dict | None:
        try:
            response = self._client.get("/status", headers=self._headers())
            if response.status_code == 200:
                return response.json()
            return None
        except httpx.RequestError:
            return None

    def get_records(self, sensor: str | None = None, limit: int = 100) -> list | None:
        try:
            params = {"limit": limit}
            if sensor:
                params["sensor"] = sensor
            response = self._client.get("/records", headers=self._headers(), params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except httpx.RequestError:
            return None

    def force_mode(self, mode: str) -> bool:
        try:
            response = self._client.post(
                "/mode/force",
                params={"mode": mode},
                headers=self._headers(),
            )
            return response.status_code == 200
        except httpx.RequestError:
            return False

    def get_forced_mode(self) -> str | None:
        try:
            response = self._client.get("/mode/forced", headers=self._headers())
            if response.status_code == 200:
                return response.json().get("forced_mode")
            return None
        except httpx.RequestError:
            return None

    def get_logs(self, lines: int = 200) -> list | None:
        try:
            response = self._client.get(
                "/logs",
                params={"lines": lines},
                headers=self._headers(),
            )
            if response.status_code == 200:
                return response.json().get("lines", [])
            return None
        except httpx.RequestError:
            return None

    def close(self):
        self._client.close()

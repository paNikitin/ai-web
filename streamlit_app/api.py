from dataclasses import dataclass, field
from typing import Any, Generator

import httpx
import streamlit as st


class BackendAPIError(RuntimeError):
    """Raised when Backend API request failed"""


@dataclass
class BackendAPI:
    base_url: str
    timeout: float = 30.0
    client: httpx.Client = field(init=False, repr=False, default_factory=httpx.Client)

    @staticmethod
    def _extract_error(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return response.text or f"HTTP status_code: {response.status_code}"

        for key in ("detail", "error", "message"):
            value = payload.get(key)
            if isinstance(value, str):
                return value

        return str(payload)

    def _request(
        self, method: str, path: str, *, api_key: str | None = None, **kwargs: Any
    ) -> httpx.Response:
        headers = dict(kwargs.pop("headers", {}))

        if api_key:
            headers["X-API-Key"] = api_key

        print(f"headers_headers:`{headers}`")

        try:
            response = self.client.request(
                method=method, url=self.base_url + path, headers=headers, **kwargs
            )
        except httpx.RequestError as e:
            raise BackendAPIError(str(e))

        if response.is_error:
            raise BackendAPIError(self._extract_error(response))

        return response

    def health(self) -> dict[str, Any]:
        payload = self._request("GET", "/health").json()
        if not isinstance(payload, dict):
            raise BackendAPIError("Backend health endpoint returns non-valid response")

        status = payload.get("status", "unknown")
        model_loaded = payload.get("model_loaded", "unknown")
        database = payload.get("database", "unknown")

        return {"status": status, "model_loaded": model_loaded, "database": database}

    def create_user(self, username: str, email: str) -> dict[str, Any]:
        payload = {"username": username, "email": email}
        return self._request("POST", "/users", json=payload).json()

    def get_user(self, user_id: str) -> dict[str, Any]:
        return self._request("GET", f"/users/{user_id}").json()

    def create_api_key(self, user_id: str, name: str) -> dict[str, Any]:
        payload = {"name": name}
        return self._request("POST", f"/users/{user_id}/api-keys", json=payload).json()

    def list_api_keys(self, user_id: str) -> dict[str, Any]:
        return self._request("GET", f"/users/{user_id}/api-keys").json()

    def create_session(self, user_id: str, api_key: str, title: str) -> dict[str, Any]:
        payload = {"title": title}
        return self._request(
            "POST", f"/users/{user_id}/sessions", json=payload, api_key=api_key
        ).json()

    def list_sessions(self, user_id: str, api_key: str) -> dict[str, Any]:
        return self._request(
            "GET", f"/users/{user_id}/sessions", api_key=api_key
        ).json()

    def get_session_history(
        self, user_id: str, api_key: str, session_id: int
    ) -> dict[str, Any]:
        return self._request(
            "GET", f"/users/{user_id}/sessions/{session_id}", api_key=api_key
        ).json()

    def get_history(
        self, user_id: str, api_key: str, limit: int = 20
    ) -> dict[str, Any]:
        payload = {"limit": limit}
        return self._request(
            "GET", f"/users/{user_id}/chat-history", api_key=api_key, params=payload
        ).json()

    def validate_auth(self, user_id: str, api_key: str) -> dict[str, Any]:
        user = self.get_user(user_id=user_id)
        self.get_history(user_id, api_key, limit=1)
        return user

    @staticmethod
    def fix_messages(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        fixed_messages = []
        for msg in messages:
            fixed_messages.append({"role": msg["role"], "message": msg["content"]})
        return fixed_messages

    def send_chat(
        self,
        api_key: str,
        session_id: int,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        payload = {
            "session_id": session_id,
            "messages": self.fix_messages(messages),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return self._request("POST", "/chat", api_key=api_key, json=payload).json()

    def stream_chat(
        self,
        api_key: str,
        session_id: int,
        messages: list[dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> Generator[str, None, None]:

        payload = {
            "session_id": session_id,
            "messages": self.fix_messages(messages),
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        print(f"messages_messages:`{messages}`")
        headers = {}
        headers["X-API-Key"] = api_key

        try:
            with self.client.stream(
                "POST", self.base_url + "/chat/stream", headers=headers, json=payload
            ) as response:
                if response.is_error:
                    response.read()
                    raise BackendAPIError(self._extract_error(response))

                for chunk in response.iter_text():
                    if chunk:
                        yield chunk
        except httpx.RequestError as e:
            raise BackendAPIError(str(e))


@st.cache_resource(show_spinner=False)
def get_api(base_url: str):
    return BackendAPI(base_url=base_url)


@st.cache_data(ttl=10, show_spinner=False)
def cached_health(base_url: str):
    return get_api(base_url=base_url).health()


@st.cache_data(ttl=10, show_spinner=False)
def cached_history(base_url: str, user_id: str, api_key: str, limit: int):
    return get_api(base_url=base_url).get_history(
        user_id=user_id, api_key=api_key, limit=limit
    )


@st.cache_data(ttl=10, show_spinner=False)
def cached_sessions(base_url: str, user_id: str, api_key: str):
    return get_api(base_url=base_url).list_sessions(user_id=user_id, api_key=api_key)


@st.cache_data(ttl=10, show_spinner=False)
def cached_session_history(base_url: str, user_id: str, api_key: str, session_id: int):
    return get_api(base_url=base_url).get_session_history(
        user_id=user_id, api_key=api_key, session_id=session_id
    )


def clear_api_caches() -> None:
    cached_health.clear()
    cached_history.clear()
    cached_sessions.clear()
    cached_session_history.clear()

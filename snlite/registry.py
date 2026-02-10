from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Dict, Any
from uuid import uuid4

from snlite.providers.base import Provider

@dataclass
class LoadedModel:
    provider_name: str
    model_id: str
    meta: Dict[str, Any]

class AppRegistry:
    """
    Thread-safe-ish registry for:
    - current provider
    - current selected model
    - streaming cancellation flags
    """
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._provider: Optional[Provider] = None
        self._loaded: Optional[LoadedModel] = None
        self._status: str = "idle"  # idle | loading | ready | error
        self._error: Optional[str] = None
        self._active_streams: Dict[str, asyncio.Event] = {}  # request_id -> cancel_event

    async def get_state(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "status": self._status,
                "error": self._error,
                "loaded": None if not self._loaded else {
                    "provider": self._loaded.provider_name,
                    "model_id": self._loaded.model_id,
                    "meta": self._loaded.meta,
                }
            }

    async def set_error(self, msg: str) -> None:
        async with self._lock:
            self._status = "error"
            self._error = msg

    async def set_loading(self) -> None:
        async with self._lock:
            self._status = "loading"
            self._error = None

    async def set_ready(self) -> None:
        async with self._lock:
            self._status = "ready"
            self._error = None

    async def set_provider_and_model(self, provider: Provider, provider_name: str, model_id: str, meta: Dict[str, Any]) -> None:
        async with self._lock:
            self._provider = provider
            self._loaded = LoadedModel(provider_name=provider_name, model_id=model_id, meta=meta)
            self._status = "ready"
            self._error = None

    async def unload(self) -> None:
        async with self._lock:
            if self._provider:
                try:
                    await self._provider.unload()
                except Exception:
                    pass
            self._provider = None
            self._loaded = None
            self._status = "idle"
            self._error = None

    async def get_provider(self) -> Optional[Provider]:
        async with self._lock:
            return self._provider

    async def get_loaded_model(self) -> Optional[LoadedModel]:
        async with self._lock:
            return self._loaded

    async def new_stream(self) -> str:
        request_id = uuid4().hex
        async with self._lock:
            self._active_streams[request_id] = asyncio.Event()
        return request_id

    async def cancel_stream(self, request_id: str) -> bool:
        async with self._lock:
            ev = self._active_streams.get(request_id)
            if not ev:
                return False
            ev.set()
            return True

    async def pop_stream(self, request_id: str) -> None:
        async with self._lock:
            self._active_streams.pop(request_id, None)

    async def is_cancelled(self, request_id: str) -> bool:
        async with self._lock:
            ev = self._active_streams.get(request_id)
            return bool(ev and ev.is_set())
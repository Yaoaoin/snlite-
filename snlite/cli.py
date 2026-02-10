from __future__ import annotations

import os
import signal
from typing import Optional

from snlite.ollama_manager import OllamaHandle, ensure_ollama_running, stop_ollama


def run():
    ollama_host = os.environ.get("SNLITE_OLLAMA_HOST", "http://127.0.0.1:11434")
    handle = OllamaHandle(host=ollama_host)

    handle = ensure_ollama_running(handle)
    if handle.started_by_snlite:
        print("[SNLite] Ollama was not running. Started `ollama serve` automatically.")
    else:
        print("[SNLite] Ollama already running. Using existing instance.")

    from snlite import main as m

    stopping = {"value": False}

    def _request_shutdown(signum: int, frame: Optional[object] = None):
        stopping["value"] = True

    try:
        try:
            signal.signal(signal.SIGINT, _request_shutdown)
            signal.signal(signal.SIGTERM, _request_shutdown)
        except Exception:
            pass

        m.run()
    finally:
        stop_ollama(handle)
        if handle.started_by_snlite:
            print("[SNLite] Stopped Ollama (started by SNLite).")
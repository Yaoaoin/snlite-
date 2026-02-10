from __future__ import annotations

import atexit
import os
import re
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional, Tuple
from urllib.parse import urlparse

import httpx


DEFAULT_OLLAMA_HOST = os.environ.get("SNLITE_OLLAMA_HOST", "http://127.0.0.1:11434")


@dataclass
class OllamaHandle:
    """Tracks an Ollama server only if started by SNLite."""
    proc: Optional[subprocess.Popen] = None             # the `ollama serve` launcher (may exit)
    server_pid: Optional[int] = None                    # the PID actually listening on 11434 (Windows)
    started_by_snlite: bool = False
    host: str = DEFAULT_OLLAMA_HOST


def _parse_host_port(host: str) -> Tuple[str, int]:
    u = urlparse(host)
    hostname = u.hostname or "127.0.0.1"
    port = u.port or 11434
    return hostname, port


def _ollama_is_alive(host: str, timeout_s: float = 0.5) -> bool:
    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.get(f"{host}/api/version")
            return r.status_code == 200
    except Exception:
        return False


def _get_listening_pid_windows(port: int) -> Optional[int]:
    """
    Return PID listening on 0.0.0.0:port or 127.0.0.1:port (TCP) using netstat.
    Example netstat line:
      TCP    127.0.0.1:11434     0.0.0.0:0      LISTENING       12345
    """
    try:
        # Use -ano so PID appears
        out = subprocess.check_output(["netstat", "-ano"], text=True, errors="ignore")
    except Exception:
        return None

    # Match LISTENING lines with :port
    pattern = re.compile(rf"^\s*TCP\s+\S+:{port}\s+\S+\s+LISTENING\s+(\d+)\s*$", re.IGNORECASE)
    for line in out.splitlines():
        m = pattern.match(line)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                return None
    return None


def _refresh_server_pid(handle: OllamaHandle) -> None:
    _, port = _parse_host_port(handle.host)
    if sys.platform.startswith("win"):
        handle.server_pid = _get_listening_pid_windows(port)
    else:
        # On non-Windows, we keep it simple: rely on proc group termination.
        handle.server_pid = None


def ensure_ollama_running(handle: OllamaHandle, wait_s: float = 10.0) -> OllamaHandle:
    """
    If Ollama already running -> do nothing.
    Else start `ollama serve` and wait until it responds.
    On Windows, record the PID actually listening on port for reliable termination.
    """
    if _ollama_is_alive(handle.host):
        handle.started_by_snlite = False
        _refresh_server_pid(handle)
        return handle

    verbose = os.environ.get("SNLITE_OLLAMA_VERBOSE", "").strip() == "1"
    stdout = None if verbose else subprocess.DEVNULL
    stderr = None if verbose else subprocess.DEVNULL

    creationflags = 0
    preexec_fn = None

    if sys.platform.startswith("win"):
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]
    else:
        preexec_fn = os.setsid  # type: ignore[assignment]

    try:
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
            preexec_fn=preexec_fn,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "Ollama executable not found. Install Ollama and ensure `ollama` is in PATH."
        ) from e

    handle.proc = proc
    handle.started_by_snlite = True

    # Ensure cleanup on interpreter exit (best effort)
    atexit.register(lambda: stop_ollama(handle))

    t0 = time.time()
    while time.time() - t0 < wait_s:
        # even if the launcher exits, server might still be alive -> do not fail early
        if _ollama_is_alive(handle.host):
            _refresh_server_pid(handle)
            return handle
        time.sleep(0.2)

    raise RuntimeError("Timed out waiting for Ollama to start.")


def _taskkill_pid_tree(pid: int) -> None:
    """
    Force-kill PID and its child process tree on Windows.
    """
    try:
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        pass


def stop_ollama(handle: OllamaHandle, timeout_s: float = 5.0) -> None:
    """
    Stop Ollama ONLY if it was started by SNLite.
    On Windows, prefer killing the PID actually listening on the server port.
    """
    if not handle.started_by_snlite:
        return

    # Refresh server pid at shutdown time (in case it changed)
    _refresh_server_pid(handle)

    if sys.platform.startswith("win"):
        # 1) If we know the real listening PID, kill that tree
        if handle.server_pid and handle.server_pid > 0:
            _taskkill_pid_tree(handle.server_pid)

        # 2) Also terminate the launcher process if still running
        if handle.proc is not None and handle.proc.poll() is None:
            try:
                handle.proc.terminate()
                handle.proc.wait(timeout=timeout_s)
            except Exception:
                try:
                    handle.proc.kill()
                except Exception:
                    pass

        return

    # Non-Windows: terminate process group if possible
    proc = handle.proc
    if proc is None:
        return

    if proc.poll() is not None:
        return

    try:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            proc.terminate()
        proc.wait(timeout=timeout_s)
    except Exception:
        try:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                proc.kill()
        except Exception:
            pass
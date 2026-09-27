"""Proxy pool. Round-robin over file-loaded entries. Thread-safe via lock."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Proxy:
    url: str
    in_use: bool = False


class ProxyPool:
    def __init__(self, proxies: list[Proxy]) -> None:
        self._proxies = proxies
        self._lock = threading.Lock()
        self._cursor = 0

    @classmethod
    def from_file(cls, path: Path) -> "ProxyPool":
        if not path.exists():
            return cls([])
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
        return cls([Proxy(url=ln) for ln in lines if ln and not ln.startswith("#")])

    def acquire(self) -> Proxy | None:
        with self._lock:
            if not self._proxies:
                return None
            for _ in range(len(self._proxies)):
                p = self._proxies[self._cursor]
                self._cursor = (self._cursor + 1) % len(self._proxies)
                if not p.in_use:
                    p.in_use = True
                    return p
            return None

    def release(self, proxy: Proxy) -> None:
        with self._lock:
            proxy.in_use = False

    def __len__(self) -> int:
        return len(self._proxies)
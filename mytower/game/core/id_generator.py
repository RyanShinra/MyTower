# Copyright (c) 2025 Ryan Osterday. All rights reserved.
# See LICENSE file for details.

import threading


class IDGenerator:

    def __init__(self, prefix: str, radix: int = 4, first_id: int = 1) -> None:
        self._prefix: str = prefix
        self._radix: int = radix
        self._next_id: int = first_id
        self._lock: threading.Lock = threading.Lock()

    def get_next_id(self) -> str:
        with self._lock:
            current_id: str = f"{self._prefix}_{self._next_id}"
            self._next_id += self._radix
            return current_id

    def reset(self, first_id: int = 1) -> None:
        with self._lock:
            self._next_id = first_id

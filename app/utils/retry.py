import time
from typing import Callable, TypeVar

T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int = 3, wait_seconds: float = 1.0) -> T:
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if i < attempts:
                time.sleep(wait_seconds * i)
    raise last_exc

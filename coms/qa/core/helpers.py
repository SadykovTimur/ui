import asyncio
import logging
import time
from typing import Any, Callable

__all__ = ['wait_for', 'await_for']

logger = logging.getLogger(__name__)


def wait_for(condition: Callable[[], Any], timeout: float = 30, poll_timeout: float = 1, msg: str = '') -> Any:
    start = time.time()
    while time.time() - start <= timeout:
        try:
            ret = condition()
            if ret:
                return ret
        except Exception as e:
            logger.warning('wait_for exception: %s', e)

        time.sleep(poll_timeout)

    raise TimeoutError(msg)


async def await_for(condition: Callable[[], Any], timeout: float = 30, poll_timeout: float = 1, msg: str = '') -> Any:
    start = time.time()
    while time.time() - start <= timeout:
        try:
            ret = await condition()
            if ret:
                return ret
        except Exception as e:
            logger.warning('await_for exception: %s', e)

        await asyncio.sleep(poll_timeout)

    raise TimeoutError(msg)

from __future__ import annotations


import asyncio
import atexit
import logging
import functools
from typing import TYPE_CHECKING

import janus

if TYPE_CHECKING:
    from typing import AsyncGenerator, Callable, Generator, List


__version__ = "0.1.3"
__all__ = ["__version__", "asyncio_generator_converter"]
logger = logging.getLogger(__name__)
tasks: List[asyncio.Task] = list()


def _cleanup_tasks() -> None:
    for _task in tasks:
        if _task.done():
            tasks.remove(_task)


def _atexit_hook() -> None:
    _cleanup_tasks()
    if len(tasks) > 0:
        print(f"{__name__} has {len(tasks)} task(s) still running")


atexit.register(_atexit_hook)


def asyncio_generator_converter(func) -> Callable:
    def _consumer(generator: Generator, queue: janus.Queue) -> None:
        logger.debug(f"starting consumer for {generator}")
        try:
            for _data in generator:
                queue.sync_q.put(_data)
        finally:
            logger.debug(f"consumer done for {generator}")

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> AsyncGenerator:
        _generator: Generator = func(*args, **kwargs)
        _queue: janus.Queue = janus.Queue(maxsize=1)
        _task = asyncio.create_task(
            asyncio.to_thread(_consumer, _generator, _queue),
            name=f"{__name__}:{_generator}",
        )
        tasks.append(_task)

        while not _task.done():
            try:
                _data = await asyncio.wait_for(_queue.async_q.get(), 1)
                yield _data
            except asyncio.TimeoutError:
                pass

        # ensure all results have been yielded
        while _queue.async_q.qsize() > 0:
            yield await _queue.async_q.get()

        try:
            await _task
        finally:
            _cleanup_tasks()

    return wrapper

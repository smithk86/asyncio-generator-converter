from __future__ import annotations

import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import TYPE_CHECKING

import janus

if TYPE_CHECKING:
    from typing import AsyncGenerator, Callable, Generator


__version__ = "0.1.1"
__all__ = ["__version__", "asyncio_generator_converter"]


def asyncio_generator_converter(func) -> Callable:
    def _consumer(generator: Generator, queue: janus.Queue) -> None:
        for _data in generator:
            queue.sync_q.put(_data)

    async def _run_consumer(executor: ThreadPoolExecutor, func: Callable):
        _loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        await _loop.run_in_executor(executor, func)

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> AsyncGenerator:
        _executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        _generator: Generator = func(*args, **kwargs)
        _queue: janus.Queue = janus.Queue(maxsize=1)
        _task: asyncio.Task = asyncio.create_task(
            _run_consumer(_executor, partial(_consumer, _generator, _queue))
        )

        try:
            while not _task.done():
                try:
                    _data = await asyncio.wait_for(_queue.async_q.get(), 1)
                    yield _data
                except asyncio.TimeoutError:
                    pass
            while _queue.async_q.qsize() > 0:
                yield await _queue.async_q.get()
        finally:
            # shutdown the executor
            _executor.shutdown()
            # throw an exception if it occured
            _task.result()

    return wrapper

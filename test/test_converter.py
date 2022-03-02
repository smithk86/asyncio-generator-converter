import asyncio
import time
from os import urandom

import pytest  # type: ignore
from asyncio_generator_converter import asyncio_generator_converter, _atexit_hook


@asyncio_generator_converter
def random_data_generator():
    for i in range(100):
        yield urandom(16)


@pytest.mark.asyncio
async def test_converter():
    _results = list()
    async for _data in random_data_generator():
        assert len(_data) == 16
        _results.append(_data)
    assert len(_results) == 100


@pytest.mark.asyncio
async def test_request_early_terminate():
    class _random_data_generator_object:
        def __init__(self):
            self.running = True

        @asyncio_generator_converter
        def __aiter__(self):
            for i in range(100):
                if self.running:
                    yield urandom(16)

    _results = list()
    _agenerator = _random_data_generator_object()
    async for _data in _agenerator:
        if len(_results) > 50:
            _agenerator.running = False
        _results.append(_data)
    assert len(_results) > 50 and len(_results) < 60


@pytest.mark.asyncio
async def test_exception():
    @asyncio_generator_converter
    def _throw_exception():
        yield urandom(16)
        yield urandom(16)
        raise Exception("this is an exception")

    with pytest.raises(Exception, match="this is an exception"):
        async for _data in _throw_exception():
            pass


@pytest.mark.asyncio
async def test_without_async():
    with pytest.raises(TypeError, match="'async_generator' object is not iterable"):
        for _data in random_data_generator():
            pass


@pytest.mark.asyncio
async def test_slow_generator():
    @asyncio_generator_converter
    def _slow_generator():
        for i in range(100):
            if i > 3:
                break
            time.sleep(2)
            yield urandom(16)

    _results = list()
    async for _data in _slow_generator():
        _results.append(_data)
    assert len(_results) == 4


@pytest.mark.asyncio
async def test_multiple_converter(capfd):
    @asyncio_generator_converter
    def _slow_generator():
        for i in range(100):
            if i > 3:
                break
            time.sleep(2)
            yield urandom(16)

    async def _consume_generator(async_gen):
        async for _ in async_gen:
            pass

    _consumers = list()
    gen1 = _slow_generator()
    await gen1.__anext__()
    _consumers.append(_consume_generator(gen1))
    gen2 = _slow_generator()
    await gen2.__anext__()
    _consumers.append(_consume_generator(gen2))
    gen3 = _slow_generator()
    await gen3.__anext__()
    _consumers.append(_consume_generator(gen3))

    _atexit_hook()
    _atexit_hook_stdout, _ = capfd.readouterr()
    assert (
        _atexit_hook_stdout.strip()
        == "asyncio_generator_converter has 3 task(s) still running"
    )

    await asyncio.gather(*_consumers)

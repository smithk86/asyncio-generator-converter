from os import urandom

import pytest  # type: ignore
from asyncio_generator_converter import asyncio_generator_converter


class random_data_generator_object:
    def __init__(self):
        self.running = True

    @asyncio_generator_converter
    def __aiter__(self):
        for i in range(100):
            if self.running:
                yield urandom(16)


@asyncio_generator_converter
def random_data_generator():
    for i in range(100):
        yield urandom(16)


@asyncio_generator_converter
def throw_exception():
    yield urandom(16)
    yield urandom(16)
    raise Exception("this is an exception")


@pytest.mark.asyncio
async def test_converter():
    _results = list()
    async for _data in random_data_generator():
        assert len(_data) == 16
        _results.append(_data)
    assert len(_results) == 100


@pytest.mark.asyncio
async def test_request_early_terminate():
    _results = list()
    _agenerator = random_data_generator_object()
    async for _data in _agenerator:
        if len(_results) > 50:
            _agenerator.running = False
        _results.append(_data)
    assert len(_results) > 50 and len(_results) < 60


@pytest.mark.asyncio
async def test_exception():
    with pytest.raises(Exception, match="this is an exception"):
        async for _data in throw_exception():
            pass


@pytest.mark.asyncio
async def test_without_async():
    with pytest.raises(TypeError, match="'async_generator' object is not iterable"):
        for _data in random_data_generator():
            pass

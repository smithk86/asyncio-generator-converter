#!/usr/bin/env python

from pathlib import Path

from setuptools import setup  # type: ignore


dir_ = Path(__file__).parent

# get the version to include in setup()
with open(f'{dir_}/asyncio_generator_converter/__init__.py') as fh:
    for line in fh:
        if '__version__' in line:
            exec(line)
            break

setup(
    name='asyncio-generator-converter',
    version=__version__,  # type: ignore
    license='MIT',
    author='Kyle Smith',
    author_email='smithk86@gmail.com',
    url='https://github.com/smithk86/asyncio-generator-converter',
    package_data={"asyncio_generator_converter": ["py.typed"]},
    packages=['asyncio_generator_converter'],
    description='convert a normal generator to an async generator with a decorator',
    install_requires=[
        'janus'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'mypy',
        'pytest',
        'pytest-asyncio',
        'pytest-mypy'
    ]
)

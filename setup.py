#!/usr/bin/env python
from setuptools import setup, find_packages


def load_long_description():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


setup(
    name='jsonier',
    version='0.1',
    description='JSON object marshalling library',
    long_description=load_long_description(),
    long_description_content_type="text/markdown",
    author='Malaya Zemlya malaya.zemlya1@gmail.com',
    author_email='dev@zemlya.ml',
    url='https://github.com/malaya-zemlya/jsonier',
    keywords=['jsonier', 'json', 'marshalling', 'serialization', 'deserialization'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    python_requires='>=3.7',
    packages=find_packages()
)

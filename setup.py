#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='mini_api',
    version=__import__('mini_api').__version__,
    author='Dario Meloni',
    author_email='mellon85@gmail.com',
    description="Minimalistic HTTP API with no frills",
    long_description="Minimalistic HTTP API with no frills",
    license='BSD 3-Clause',
    url="https://github.com/mellon85/mini-api",
    packages=find_packages(exclude=('tests*',)),
    test_suite='tests',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    )
)

#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='mini_api',
    version=__import__('mini_api').__version__,
    author='Dario Meloni',
    author_email='mellon85@gmail.com',
    license='LGPL',
    packages=find_packages(exclude=('tests*',)),
    test_suite='tests',
)

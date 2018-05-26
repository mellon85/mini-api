#!/usr/bin/env python
from setuptools import find_packages, setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mini_api',
    version=__import__('mini_api').__version__,
    author='Dario Meloni',
    author_email='mellon85@gmail.com',
    description="Minimalistic HTTP API with no frills",
    long_description=long_description,
    long_description_content_type='text/markdown',
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

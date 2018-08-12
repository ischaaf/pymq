import os
from setuptools import setup, find_packages


setup(
    name="pymq",
    version="0.1.0",
    author="Isaac Schaaf",
    author_email="zeekus99@gmail.com",
    description=("A queue wrapper library for python"),
    license="Apache-2.0",
    keywords="queue message-queue",
    packages=find_packages(exclude=('examples',)),
)

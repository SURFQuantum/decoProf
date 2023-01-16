#!/usr/bin/env python

# from distutils.core import setup
from setuptools import setup, find_packages
import decoProf.info as dp_info

NAME = dp_info.PACKAGE_NAME
VERSION = dp_info.PACKAGE_VERSION
HOMEPAGE = dp_info.PACKAGE_HOMEPAGE

setup(
    name=NAME,
    version=VERSION,
    description='Profiler aggregator',
    author='Maxim Masterov',
    author_email='maksim.masterov@surf.nl',
    url=HOMEPAGE,
    install_requires=[
        'pycg',
        'astunparse',
        'pyinstrument',
        'yappi',
        'memory_profiler',
        'line-profiler',
    ],
    packages=find_packages('.'),
    py_modules=[NAME],
    license='MIT',
    long_description='{} is a small wrapper script that allows '
                     'profiling Python packages in a simple and intuitive '
                     'manner.'.format(NAME),
    entry_points={
        'console_scripts': [
            '{} = {}.{}:main'.format(NAME, NAME, NAME),
        ],
    },
)

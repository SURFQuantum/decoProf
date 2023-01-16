#!/usr/bin/env python
from setuptools import setup, find_packages
from decoProf.info import PACKAGE_VERSION, PACKAGE_NAME, PACKAGE_HOMEPAGE


setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='Profiler aggregator',
    author='Maxim Masterov',
    author_email='maksim.masterov@surf.nl',
    url=PACKAGE_HOMEPAGE,
    install_requires=[
        'pycg',
        'astunparse',
        'pyinstrument',
        'yappi',
        'memory_profiler',
        'line-profiler',
    ],
    packages=[PACKAGE_NAME],
    py_modules=[PACKAGE_NAME],
    license='MIT',
    long_description='{} is a small wrapper script that allows '
                     'profiling Python packages in a simple and intuitive '
                     'manner.'.format(PACKAGE_NAME),
    entry_points={
        'console_scripts': [
            '{} = {}.{}:main'.format(PACKAGE_NAME, PACKAGE_NAME, PACKAGE_NAME),
        ],
    },
)

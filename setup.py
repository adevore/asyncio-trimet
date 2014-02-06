#!/usr/bin/env python

from setuptools import setup
import sys

requires = ['aiohttp']

if sys.version_info < (3, 4):
    requires.append('asyncio')

setup(name='asyncio-trimet',
      version="0.1",
      description="Trimet tracker support for asyncio",
      author="Aaron DeVore",
      author_email="aaron.devore@gmail.com",
      classifiers=[
          'Programming Language :: Python 3.3',
          'Programming Language :: Python 3.4',
        ],
      packages=['aiotrimet'],
      install_requires=['asyncio', 'aiohttp'],
      entry_points = {
          'console_scripts': [
              'trimet-arrivals = scripts.arrivals:main',
              'trimet-nearby = scripts.nearby:main',
              ]
          },
      #license=,
)
      

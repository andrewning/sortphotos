#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages
import sys

if sys.version_info.major is 3:
    sys.exit('Sorry, Python 3 is not supported')

setup(
    name='sortphotos',
    version='1.0',
    description='Organizes photos and videos into folders using date/time information ',
    author='Andrew Ning',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    entry_points={
        'console_scripts': [
          'sortphotos = src.sortphotos:main',
        ]
      }
)


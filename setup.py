# !/usr/bin/env python

from setuptools import setup, find_packages

setup(name='sortphotos',
      version='0.1',
      packages=find_packages(),
      package_data={
      },
      install_requires=[
      ],
      entry_points={
          'console_scripts': [
            'sortphotos = src.sortphotos:main',
          ]
      })

#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='jencrypt',
      version='2.0.5',
      description='File and directory encryption tool for automatically mounting data volumes',
      author='JamesZBL',
      author_email='zhengbaole@gmail.com',
      url='https://github.com/JamesZBL/jencrypt',
      packages=find_packages(),
      python_requires='>=3',
      entry_points={
          'console_scripts': [
              'jencrypt = app.bootstrap:main'
          ]
      },
      )

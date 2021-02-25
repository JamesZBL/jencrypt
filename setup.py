#!/usr/bin/env python3
import pathlib

from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='jencrypt',
      version='2.0.16',
      description='File and directory encryption tool with automatically mounting data volumes',
      long_description=README,
      long_description_content_type="text/markdown",
      author='JamesZBL',
      author_email='zhengbaole@gmail.com',
      license='Apache2',
      url='https://github.com/JamesZBL/jencrypt',
      packages=find_packages(),
      install_requires=['watchdog'],
      python_requires='>=3',
      entry_points={
          'console_scripts': [
              'jencrypt = jencrypt.bootstrap:main'
          ]
      },
      )

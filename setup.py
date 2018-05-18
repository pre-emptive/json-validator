from distutils.core import setup
import glob
import os

setup(
    name='jsonvalidator',
    url='https://github.com/pre-emptive/json-validator',
    author='Ralph Bolton',
    author_email='devnull@coofercat.com',
    version='1.0.0',
    packages=['jsonvalidator'],
    license='GPLv2',
    long_description=open('README.md').read(),
)

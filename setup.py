#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckantest
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'0.1.0'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

setup(
    name=u'ckantest',
    version=__version__,
    description=u'Helpers for testing CKAN extensions.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN testing',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckantest',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    include_package_data=True,
    install_requires=[]
    )

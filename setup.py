#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup (
	name='astvcardcallerid',
	version="0.10",
	description="Asterisk VCard Caller ID Lookup",
	author='Dr. Torge Szczepanek',
	author_email='debian@cygnusnetworks.de',
	license='Apache License 2.0',
	entry_points={'console_scripts': ['astvcardcallerid = astvcardcallerid.fastagi:main']},
	packages=['astvcardcallerid'],
	install_requires=["configobj", "vobject", "phonenumbers"],
)

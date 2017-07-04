#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup (
	name='ast-vcard-callerid',
	version="0.10",
	description="Asterisk VCard Caller ID Lookup",
	author='Dr. Torge Szczepanek',
	author_email='debian@cygnusnetworks.de',
	license='Apache License 2.0',
	entry_points={'console_scripts': ['ast-vcard-callerid = astvcardcallerid.fastagi:main']},
	packages=['astvcardcallerid'],
	install_requires=["configobj", "vobject", "phonenumbers"],
)

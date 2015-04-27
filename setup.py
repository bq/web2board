#!/usr/bin/python
# coding=utf-8

import os
from setuptools import setup, find_packages

def package_data_dirs(source, sub_folders):
	dirs = []

	for d in sub_folders:
		for dirname, _, files in os.walk(os.path.join(source, d)):
			dirname = os.path.relpath(dirname, source)
			for f in files:
				dirs.append(os.path.join(dirname, f))
	return dirs

setup(name='Web2board',
      version='0.0.1',
      author='bitbloq team',
      author_email='bitbloq@bq.com',
      description='Native program that connects a website and a board.',

      license='GPLv2',
      keywords = "bitbloq web2board arduino robotics",
      url='https://www.diwo.bq.com',

      packages = ['web2board'],
      package_dir = {'web2board': '.'},
      package_data = {'web2board': package_data_dirs('.', ['doc', 'res', 'src'])},
      
      scripts=['pkg/linux/web2board'],
      data_files=[('/usr/share/applications', ['pkg/linux/web2board.desktop'])]
     )
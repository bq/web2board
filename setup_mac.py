# coding=utf-8
import os
from setuptools import setup

def package_data_dirs(source, sub_folders):
	dirs = []

	for d in sub_folders:
		for dirname, _, files in os.walk(os.path.join(source, d)):
			dirname = os.path.relpath(dirname, source)
			for f in files:
				dirs.append(os.path.join(dirname, f))
	return dirs

APP = ['src/web2board.py']
DATA_FILES = ['src/res','src/SerialMonitor.py']

setup(
    author='bq',
    name='Web2Board',
    author_email='support-bitbloq@bq.com',
    description='Native program that connects a web and a board. It compiles Arduino sketches and uploads them onto an Arduino board.',
    license='GNU GPL',
    keywords="web2board bitbloq arduino compile upload",
    url='https://github.com/bq/web2board',
    app=APP,
    data_files=DATA_FILES,
    options=dict(py2app=dict(
    					plist='Info.plist')
    ),
    packages =['web2board'],
    package_dir = {'web2board': 'src'},
    package_data = {
      'web2board': package_data_dirs('src', ['.'])
    },
    setup_requires=['py2app']
)

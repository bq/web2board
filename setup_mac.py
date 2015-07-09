# coding=utf-8

import os
from setuptools import setup

version = os.environ.get('VERSION')

APP = ['src/horus.py']
DATA_FILES = ['res']

PLIST = {
    u'CFBundleName': u'Horus',
    u'CFBundleShortVersionString': '0.0.1',
    u'CFBundleVersion': '0.0.1',
    u'CFBundleIdentifier': u'com.bq.Horus-0.0.1',
    u'LSMinimumSystemVersion': u'10.8',
    u'LSApplicationCategoryType': u'public.app-category.graphics-design'
  }

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'res/horus.icns',
    'plist': PLIST
  }

setup(name='Horus',
      version=version,
      author='Jesús Arroyo Torrens',
      author_email='jesus.arroyo@bq.com',
      description='Horus is a full software solution for 3D scanning',
      license='GPLv2',
      keywords="horus ciclop scanning 3d",
      url='https://www.diwo.bq.com/tag/ciclop',
      app=APP,
      data_files=DATA_FILES,
      options={'py2app': OPTIONS},
      setup_requires=['py2app'])
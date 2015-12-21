#!/usr/bin/python
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


def version():
    import sys, json;
    f = open('res/common/config.json')
    ret = json.load(f)["version"]
    return str(ret)


setup(
    name='web2board',
    version=version(),
    author='bitbloq team',
    author_email='support-bitbloq@bq.com',
    platforms=['any'],
    description='Native program that connects a website and a board.',
    license='GPLv2',
    keywords="bitbloq web2board arduino robotics",
    url='https://github.com/bq/web2board',

    packages=['web2board'],
    package_dir={'web2board': 'src'},
    package_data={
        'web2board': package_data_dirs('src', ['.'])
    },

    scripts=['pkg/linux/web2board'],
    data_files=[('/usr/share/applications', ['pkg/linux/web2board.desktop'])]
)

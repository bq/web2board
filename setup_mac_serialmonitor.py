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

setup(
    author='bq',
    name='SerialMonitor',
    author_email='support-bitbloq@bq.com',
    description='Serial Monitor.',
    license='GNU GPL',
    keywords="serialmonitor web2board bitbloq arduino compile upload",
    url='https://github.com/bq/web2board',
    app=['src/SerialMonitor.py'],
    data_files=['src/res/config.json','src/res/web2board.icns'],
    options=dict(py2app=dict(
    					plist='serialMonitor_Info.plist')
    ),
    packages =['SerialMonitor'],
    package_dir = {'SerialMonitor': 'src'},
    package_data = {
      'SerialMonitor': package_data_dirs('src', [])
    },
    setup_requires=['py2app']
)

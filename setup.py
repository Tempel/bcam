#!/usr/bin/env python2

from setuptools import setup

setup(
    name='BCAM',
    version='0.3.1',
    description='CAM system for hobbyists',
    long_description=open('README.md').read(),
    author='Konstantin Kirik',
    url='http://hobbycam.org/',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: GTK',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
    install_requires=['dxfgrabber'], # Also requires pygtk>=2, but that can't
                                     # be automatically installed by pip.
    packages=['bcam'],
    entry_points={'gui_scripts': ['bcam = bcam.main:main']},
)

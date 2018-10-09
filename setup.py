# -*- coding: utf-8 -*-

import os
import platform
import sys

import setuptools

# check platform
if platform.system() != 'Darwin':
    class UnsupportedOS(RuntimeError):
        def __init__(self, message, *args, **kwargs):
            sys.tracebacklimit = 0
            super().__init__(message, *args, **kwargs)
    raise UnsupportedOS('macdaily: script runs only on macOS')

# version
__version__ = '2018.09.28'

# README
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as file:
    long_desc = file.read()

# set-up script for pip distribution
setuptools.setup(
    name='macdaily',
    version=__version__,
    author='Jarry Shaw',
    author_email='jarryshaw@icloud.com',
    url='https://github.com/JarryShaw/macdaily#macdaily',
    license='GNU General Public License v3 (GPLv3)',
    keywords='daily utility script',
    description='Package day-care manager on macOS.',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    python_requires='>=3.4',
    install_requires=['setuptools'],
    extras_require={
        'pipdeptree': ['pipdeptree'],
        ':python_version == "3.4"': ['pathlib2', 'subprocess32'],
    },
    entry_points={
        'console_scripts': [
            'macdaily = macdaily.__main__:main',
            'md-update = macdaily.daily_update:main',
            'md-uninstall = macdaily.daily_uninstall:main',
            'md-reinstall = macdaily.daily_reinstall:main',
            'md-postinstall = macdaily.daily_postinstall:main',
            'md-logging = macdaily.daily_logging:main',
            'md-dependency = macdaily.daily_dependency:main',
            'md-bundle = macdaily.daily_bundle:main',
            'md-config = macdaily.daily_config:main',
            'md-archive = macdaily.daily_archive:main',
        ]
    },
    packages=[
        'macdaily',
        'macdaily.libbundle',
        'macdaily.libupdate',
        'macdaily.libuninstall',
        'macdaily.libprinstall',
        'macdaily.libdependency',
        'macdaily.liblogging',
    ],
    package_data={
        '': [
            'LICENSE',
            'README',
        ],
        'macdaily': ['*.py', '*.sh'],
        'macdaily.libbundle': ['*.py', '*.sh'],
        'macdaily.libupdate': ['*.py', '*.sh'],
        'macdaily.libuninstall': ['*.py', '*.sh'],
        'macdaily.libprinstall': ['*.py', '*.sh'],
        'macdaily.libdependency': ['*.py', '*.sh'],
        'macdaily.liblogging': ['*.py', '*.sh'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Unix Shell',
        'Topic :: Utilities',
    ]
)

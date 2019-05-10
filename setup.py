#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import os.path

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

with open(os.path.join('on_the_fly','VERSION')) as version_file:
    version = version_file.read().strip()

requirements = [
    # Add your project's requirements here, e.g.,
    # 'astra-toolbox',
    # 'sacred>=0.7.2',
    # 'tables==3.4.4',
]

setup_requirements = [ ]

test_requirements = [ ]

dev_requirements = [
    'autopep8',
    'rope',
    'jedi',
    'flake8',
    'importmagic',
    'autopep8',
    'black',
    'yapf',
    'snakeviz',
    # Documentation
    'sphinx',
    'sphinx_rtd_theme',
    'recommonmark',
    # Other
    'watchdog',
    'coverage',

    ]

setup(
    author="Allard Hendriksen",
    author_email='allard.hendriksen@cwi.nl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="On the fly machine learning for improving image resolution in tomography",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='on_the_fly',
    name='on_the_fly',
    entry_points='''
        [console_scripts]
        otf-project=on_the_fly.project:entry_main
        otf-display=on_the_fly.display:entry_main
        otf-normalize=on_the_fly.normalize:entry_main
        otf-reconstruct=on_the_fly.reconstruct:entry_main
        otf-subtract=on_the_fly.subtract:entry_main
        otf-extract=on_the_fly.extract:entry_main
        otf-resample=on_the_fly.resample:entry_main
        otf-train=on_the_fly.train:entry_main
        otf-process=on_the_fly.process:entry_main
    ''',
    packages=find_packages(include=['on_the_fly']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    extras_require={ 'dev': dev_requirements },
    url='https://github.com/ahendriksen/on_the_fly',
    version=version,
    zip_safe=False,
)

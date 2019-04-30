# -*- coding: utf-8 -*-

"""Top-level package for On the fly machine learning for improving image resolution in tomography."""

__author__ = """Allard Hendriksen"""
__email__ = 'allard.hendriksen@cwi.nl'


def __get_version():
    import os.path
    version_filename = os.path.join(os.path.dirname(__file__), 'VERSION')
    with open(version_filename) as version_file:
        version = version_file.read().strip()
    return version


__version__ = __get_version()

# Import all definitions from main module.
from .on_the_fly import *

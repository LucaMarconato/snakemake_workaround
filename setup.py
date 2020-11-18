#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
===============================
HtmlTestRunner
===============================


.. image:: https://img.shields.io/pypi/v/snakemake_workaround.svg
        :target: https://pypi.python.org/pypi/snakemake_workaround
.. image:: https://img.shields.io/travis/LucaMarconato/snakemake_workaround.svg
        :target: https://travis-ci.org/LucaMarconato/snakemake_workaround

Workaround for this bug/feature request: https://github.com/snakemake/snakemake/issues/660


Links:
---------
* `Github <https://github.com/LucaMarconato/snakemake_workaround>`_
"""

from setuptools import setup, find_packages

requirements = ['Click>=6.0', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Luca Marconato",
    author_email='luca.marconato@embl.de',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Workaround for this bug/feature request: https://github.com/snakemake/snakemake/issues/660",
    entry_points={
        'console_scripts': [
            'snakemake_workaround=snakemake_workaround.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=__doc__,
    include_package_data=True,
    keywords='snakemake_workaround',
    name='snakemake_workaround',
    packages=find_packages(include=['snakemake_workaround']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/LucaMarconato/snakemake_workaround',
    version='0.1.0',
    zip_safe=False,
)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics
# SPDX-License-Identifier: GPL-3.0-only
from codecs import open
from setuptools import setup, find_packages

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', 'utf-8') as f:
    required = f.read().splitlines()

if __name__ == "__main__":
    setup(
        name='fosslight_reuse',
        version='2.1.7',
        package_dir={"": "src"},
        packages=find_packages(where='src'),
        description='FOSSLight Reuse',
        long_description=readme,
        long_description_content_type='text/markdown',
        license='GPL-3.0-only',
        author='LG Electronics',
        url='https://github.com/fosslight/fosslight_reuse',
        download_url='https://github.com/fosslight/fosslight_reuse',
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9"],
        install_requires=required,
        package_data={'fosslight_reuse': ['resources/convert_license.json']},
        include_package_data=True,
        entry_points={
            "console_scripts": [
                "fosslight_reuse = fosslight_reuse.cli:main"
            ]
        }
    )

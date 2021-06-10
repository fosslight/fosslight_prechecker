#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics
# SPDX-License-Identifier: Apache-2.0
from codecs import open
from setuptools import setup, find_packages

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', 'utf-8') as f:
    required = f.read().splitlines()

if __name__ == "__main__":
    setup(
        name='fosslight_reuse',
        version='1.0.1',
        package_dir={"": "src"},
        packages=find_packages(where='src'),
        description='Wrapper of reuse lint.',
        long_description=readme,
        long_description_content_type='text/markdown',
        license='LGE-Proprietary',
        author='Soim Kim',
        author_email='soim.kim@lge.com',
        url='http://mod.lge.com/code/projects/OSC/repos/fosslight_reuse',
        download_url='http://mod.lge.com/code/rest/archive/latest/projects/OSC/repos/fosslight_reuse/archive?format=zip',
        classifiers=['Programming Language :: Python :: 3.6',
                     'License :: OSI Approved :: Closed Sorce Software'],
        install_requires=required,
        entry_points={
            "console_scripts": [
                "fosslight_reuse = fosslight_reuse.wrapper_reuse_lint:main"
            ]
        }
    )

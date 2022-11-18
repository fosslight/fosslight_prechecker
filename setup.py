#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics
# SPDX-License-Identifier: GPL-3.0-only
from codecs import open
import os
import shutil
from setuptools import setup, find_packages

with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', 'utf-8') as f:
    required = f.read().splitlines()

_PACKAEG_NAME = 'fosslight_prechecker'
_LICENSE_FILE = 'LICENSE'
_LICENSE_DIR = 'LICENSES'

if __name__ == "__main__":
    dest_path = os.path.join('src', _PACKAEG_NAME, _LICENSE_DIR)
    try:
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)
        if os.path.isfile(_LICENSE_FILE):
            shutil.copy(_LICENSE_FILE, dest_path)
        if os.path.isdir(_LICENSE_DIR):
            license_f = [f_name for f_name in os.listdir(_LICENSE_DIR) if f_name.upper().startswith(_LICENSE_FILE)]
            for lic_f in license_f:
                shutil.copy(os.path.join(_LICENSE_DIR, lic_f), dest_path)
    except Exception as e:
        print(f'Warning: Fail to copy the license text: {e}')

    setup(
        name='fosslight_prechecker',
        version='3.0.11',
        package_dir={"": "src"},
        packages=find_packages(where='src'),
        description='FOSSLight Prechecker',
        long_description=readme,
        long_description_content_type='text/markdown',
        license='GPL-3.0-only',
        author='LG Electronics',
        url='https://github.com/fosslight/fosslight_prechecker',
        download_url='https://github.com/fosslight/fosslight_prechecker',
        classifiers=[
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9"],
        install_requires=required,
        package_data={_PACKAEG_NAME: ['resources/convert_license.json', os.path.join(_LICENSE_DIR, '*')]},
        include_package_data=True,
        entry_points={
            "console_scripts": [
                "fosslight_prechecker = fosslight_prechecker.cli:main",
                "fosslight_reuse = fosslight_prechecker.cli:main"
            ]
        }
    )
    shutil.rmtree(dest_path, ignore_errors=True)

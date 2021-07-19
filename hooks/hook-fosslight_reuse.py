#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('fosslight_reuse')

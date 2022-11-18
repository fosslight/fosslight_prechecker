#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import multiprocessing
from fosslight_prechecker.cli import main

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()

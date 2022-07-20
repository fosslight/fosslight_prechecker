#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_REUSE = """
    FOSSLight Reuse is a Tool to check REUSE compliance in source code.

    Usage: fosslight_reuse [Mode] [option1] <arg1> [option2] <arg2>...
     ex) fosslight_reuse lint -p /home/test/src/
         fosslight_reuse add -p /home/test/test.py -c "2019-2021 LG Electronics Inc." -l "GPL-3.0-only"

    Parameters:
        Mode
            lint\t\t    Check REUSE compliance
            convert\t\t    Convert oss_pkg_info.yaml <-> FOSSLight-Report.xlsx
            add\t\t\t    Add missing license and copyright

        Options:
            -h\t\t\t    Print help message
            -v\t\t\t    Print FOSSLight Prechecker version
            -p <path>\t\t    Path to check
            -f <format>\t\t    Result format(yaml, xml, html)
            -o <file_name>\t    Output file name
            -n\t\t\t    Don't exclude venv*, node_modules, and .*/ from the analysis
            -i\t\t\t    Don't both write log file and show progress bar

        Options for only 'add' mode
            -l <license>\t    License name(SPDX format) to add
            -c <copyright>\t    Copyright to add(ex, 2015-2021 LG Electronics Inc.)

        Options for only 'convert' mode
            -s <sheet_names>\t    Sheet name in excel to change to yaml(ex. SRC,BIN)"""


def print_help_msg(exitOpt=True):
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_REUSE)
    helpMsg.print_help_msg(exitOpt)

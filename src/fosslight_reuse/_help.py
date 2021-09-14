#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_REUSE = """
    Usage: fosslight_reuse [Mode] [option1] <arg1> [option2] <arg2>...
        ex) fosslight_reuse lint -p /home/test/ -f "notice/sample.py,src/init.py"
            fosslight_reuse add -a -l MIT -c LGE

    FOSSLight Reuse is a Tool to check REUSE compliance in source code.

    Parameters:
        Mode
            lint\t\t    Check REUSE compliance
            report\t\t    oss_pkg_info.yaml <-> FOSSLight-Report.xml
            add\t\t\t    Add missing license and copyright

        Options:
            -h\t\t\t    Print help message
            -p <path>\t\t    Path to check
            -f <file1,file2,..>\t    List of files to check
            -o <file_name>\t    Output file name
            -n\t\t\t    Don't exclude venv*, node_modules, and .*/ from the analysis
        Options for only 'add' mode
            -l <license>\t    License name(SPDX format) to add
            -c <copyright>\t    Copyright to add(ex, "Copyright 2015-2021 LGE Electronics")
            -m\t\t\t    Add manually your input license and copyright (using without -l or -c option)  """


def print_help_msg(exitOpt=True):
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_REUSE)
    helpMsg.print_help_msg(exitOpt)

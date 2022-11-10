#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
from fosslight_util.help import PrintHelpMsg


_HELP_MESSAGE_PRECHECKER = """
    FOSSLight Prechecker is a tool that checks whether source code complies with copyright and license writing rules.

    Usage: fosslight_prechecker [Mode] [option1] <arg1> [option2] <arg2>...
     ex) fosslight_prechecker lint -p /home/test/src/
         fosslight_prechecker add -p /home/test/test.py -c "2019-2021 LG Electronics Inc." -l "GPL-3.0-only"
         fosslight_prechecker convert -p /home/test/sbom_info.py

    Parameters:
        Mode
            lint\t\t    (Default) Check whether the copyright and license writing rules are complied with
            convert\t\t    Convert sbom_info.yaml -> FOSSLight-Report.xlsx
            add\t\t\t    Add missing license and copyright

        Options:
            -h\t\t\t    Print help message
            -v\t\t\t    Print FOSSLight Prechecker version
            -p <path>\t\t    Path to check(Default: current directory)
            -f <format>\t\t    Result format(yaml, xml, html)
            -o <file_name>\t    Output file name
            -i\t\t\t    Don't both write log file and show progress bar
            --notice\t\t    Print the open source license notice text.

        Option for only 'lint' mode
            -n\t\t\t    Don't exclude venv*, node_modules, .*/, and the result of FOSSLight Scanners from the analysis

        Options for only 'add' mode
            -l <license>\t    License name(SPDX format) to add
            -c <copyright>\t    Copyright to add(ex, 2015-2021 LG Electronics Inc.)"""


def print_help_msg(exitOpt=True):
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_PRECHECKER)
    helpMsg.print_help_msg(exitOpt)

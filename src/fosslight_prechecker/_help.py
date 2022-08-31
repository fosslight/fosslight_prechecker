#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import logging
import fosslight_util.constant as constant
from fosslight_util.help import PrintHelpMsg

logger = logging.getLogger(constant.LOGGER_NAME)


_HELP_MESSAGE_PRECHECKER = """
    FOSSLight Prechecker is a tool that checks whether source code complies with copyright and license writing rules.

    Usage: fosslight_prechecker [Mode] [option1] <arg1> [option2] <arg2>...
     ex) fosslight_prechecker lint -p /home/test/src/
         fosslight_prechecker add -p /home/test/test.py -c "2019-2021 LG Electronics Inc." -l "GPL-3.0-only"
         fosslight_prechecker convert -p /home/test/sbom_info.py

    Parameters:
        Mode
            lint\t\t    Check whether the copyright and license writing rules are complied with
            convert\t\t    Convert sbom_info.yaml -> FOSSLight-Report.xlsx
            add\t\t\t    Add missing license and copyright

        Options:
            -h\t\t\t    Print help message
            -v\t\t\t    Print FOSSLight Prechecker version
            -p <path>\t\t    Path to check(Default: current directory)
            -f <format>\t\t    Result format(yaml, xml, html)
            -o <file_name>\t    Output file name
            -n\t\t\t    Don't exclude venv*, node_modules, and .*/ from the analysis
            -i\t\t\t    Don't both write log file and show progress bar

        Options for only 'add' mode
            -l <license>\t    License name(SPDX format) to add
            -c <copyright>\t    Copyright to add(ex, 2015-2021 LG Electronics Inc.)"""


def print_help_msg(exitOpt=True):
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_PRECHECKER)
    helpMsg.print_help_msg(exitOpt)


def print_invalid_msg(reason: str):
    logger.warning(f"fosslight_prechecker: {reason}")
    logger.warning("fosslight_prechecker [Mode] [option1] <arg1> [option2] <arg2>...")
    logger.warning("Try 'fosslight_prechecker -h' for more information")

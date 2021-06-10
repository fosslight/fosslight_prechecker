#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
from fosslight_util.help import PrintHelpMsg

_HELP_MESSAGE_REUSE = """
    Usage: fosslight_reuse [option1] <arg1> [option2] <arg2>...
        ex) fosslight_reuse -p /home/test/ -f "notice/sample.py,src/init.py"

    FOSSLight Reuse is a Tool to check REUSE compliance in source code by using https://github.com/fsfe/reuse-tool.

    Options:
        Mandatory
            -p <source_path>        Source path to check

        Optional
            -h\t\t\t    Print help message
            -n\t\t\t    Don't exclude venv*, node_modules, and .*/ from the analysis
            -r <file_name>\t    Xml format result file name (Default : reuse_checker.xml)
            -f <file1,file2,..>\t    List of files to check copyright and license """


def print_help_msg(exitOpt=True):
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_REUSE)
    helpMsg.print_help_msg(exitOpt)

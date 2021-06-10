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
            -n\t\t\t    If you do not want to use the Default REUSE dep5 file, add this parameter
                              \t\t- Default REUSE dep5 file function:
                              \t\t    exclude venv*/, node_modules,.*/ Folders, .json and binary file from reuse lint
            -r <file_name>\t    File name to save the result in xml format. (Default : reuse_checker.xml)
            -f <file_list>\t    List of files to check if license information is not included. (Separator : ,)"""


def print_help_msg(exitOpt=True):
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_REUSE)
    helpMsg.print_help_msg(exitOpt)

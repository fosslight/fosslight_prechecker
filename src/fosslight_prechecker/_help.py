#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
from fosslight_util.help import PrintHelpMsg


_HELP_MESSAGE_PRECHECKER = """
    FOSSLight Prechecker is a tool that checks whether source code complies with copyright and license writing rules.

    Usage: fosslight_prechecker [Mode] [option1] <arg1> [option2] <arg2>...
     ex) fosslight_prechecker lint -p /home/test/src/
         fosslight_prechecker lint -p /home/test/src/ -e test.py dep/temp
         fosslight_prechecker add -p /home/test/test.py -c "2019-2021 LG Electronics Inc." -l "GPL-3.0-only"
         fosslight_prechecker convert -p /home/test/sbom_info.yaml
         fosslight_prechecker download -l "MIT"

    Parameters:
        Mode
            lint\t\t    (Default) Check whether the copyright and license writing rules are complied with
            convert\t\t    Convert sbom_info.yaml -> FOSSLight-Report.xlsx
            add\t\t\t    Add missing license, copyright, and download url
            download\t\t    Download the license text of the license specified in sbom-info.yaml

        Options:
            -h\t\t\t    Print help message
            -v\t\t\t    Print FOSSLight Prechecker version
            -p <path>\t\t    Path to check(Default: current directory)
            -e <path>\t\t    Path to exclude from checking(only work with 'lint' mode)
            -f <format>\t\t    Result format(yaml, xml, html)
            -o <file_name>\t    Output file name
            -i\t\t\t    Don't both write log file and show progress bar
            --notice\t\t    Print the open source license notice text.

        Option for 'lint' mode
            -n\t\t\t    Don't exclude venv*, node_modules, .*/, and the result of FOSSLight Scanners from the analysis

        Options for 'add' mode
            Please enter any argument with double quotation marks("").
            -l <license>\t    License name(SPDX format) to add(ex, "Apache-2.0")
            -c <copyright>\t    Copyright to add(ex, "2015-2021 LG Electronics Inc.")
            -u <dl_location>\t    Download Location to add(ex, "https://github.com/fosslight/fosslight_prechecker")

        Options for 'download' mode
            Please enter any argument with double quotation marks("").
            -l <license>\t    License to be representative license
        """

def print_help_msg(exitOpt: bool = True) -> None:
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_PRECHECKER)
    helpMsg.print_help_msg(exitOpt)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
from fosslight_util.help import PrintHelpMsg


_HELP_MESSAGE_PRECHECKER = """
    📖 Usage
    ────────────────────────────────────────────────────────────────────
    fosslight_prechecker [mode] [options] <arguments>

    📝 Description
    ────────────────────────────────────────────────────────────────────
    FOSSLight Prechecker checks and corrects copyright and license writing
    rules in source code. It can lint, add, convert, and
    download license information.

    📚 Guide: https://fosslight.org/fosslight-guide/scanner/1_prechecker.html

    🔧 Modes
    ────────────────────────────────────────────────────────────────────
    lint (default)         Check copyright and license writing rules compliance
    add                    Add missing license, copyright, and download location
    convert                Convert sbom-info.yaml to FOSSLight-Report.xlsx
    download               Download license text specified in sbom-info.yaml

    ⚙️  General Options
    ────────────────────────────────────────────────────────────────────
    -p <path>              Path to check (default: current directory)
    -o <file>              Output file name
    -f <format>            Result format (yaml, xml, html)
    -e <pattern>           Exclude paths from checking (files and directories)
                           (only works with 'lint' mode)
                           ⚠️  IMPORTANT: Always wrap in quotes to avoid shell expansion
                           Example: fosslight_prechecker -e "test/" "*.pyc"
    -h                     Show this help message
    -v                     Show version information
    -i                     Don't write log file and show progress bar
    --notice               Print the open source license notice text

    🔍 Mode-Specific Options
    ────────────────────────────────────────────────────────────────────
    lint mode:
      -n                   Don't exclude venv*, node_modules, .*/, and
                           FOSSLight Scanner results from analysis

    add mode:
      -l <license>         Add license name in SPDX format (ex: "Apache-2.0")
      -c <copyright>       Add copyright text (ex: "2015-2021 LG Electronics Inc.")
      -u <url>             Add download location URL(ex: "https://www.sampleurl.com")

    download mode:
      -l <license>         License to be representative license

    💡 Examples
    ────────────────────────────────────────────────────────────────────
    # Lint current directory (check compliance)
    fosslight_prechecker lint

    # Lint specific path with exclusions
    fosslight_prechecker lint -p /path/to/source -e "test/" "node_modules/"

    # Add license and copyright to a file
    fosslight_prechecker add -p test.py -l "GPL-3.0-only" -c "2019-2021 LG Electronics Inc."

    # Add license, copyright, and download location
    fosslight_prechecker add -p src/main.py -l "Apache-2.0" -c "2023 MyCompany" -u "https://github.com/user/repo"

    # Convert sbom-info.yaml to Excel report
    fosslight_prechecker convert -p sbom-info.yaml

    # Download license text
    fosslight_prechecker download -l "MIT"
    """


def print_help_msg(exitOpt: bool = True) -> None:
    helpMsg = PrintHelpMsg(_HELP_MESSAGE_PRECHECKER)
    helpMsg.print_help_msg(exitOpt)

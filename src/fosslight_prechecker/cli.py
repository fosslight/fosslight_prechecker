#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import sys
import os
import logging
import fosslight_util.constant as constant
from fosslight_util.help import print_package_version
from fosslight_prechecker._help import print_help_msg, print_invalid_msg
from fosslight_prechecker._precheck import run_lint, PKG_NAME
from fosslight_oss_pkg._convert import convert_report
from fosslight_prechecker._add import add_content

logger = logging.getLogger(constant.LOGGER_NAME)


def main():
    parser = argparse.ArgumentParser(description='FOSSLight Prechecker', prog='fosslight_prechecker', add_help=False)
    parser.add_argument('mode', nargs='?', help='lint | convert | add', default="")
    parser.add_argument('--path', '-p', help='Path to check', type=str, dest='path', default="")
    parser.add_argument('--format', '-f', help='Format of ouput', type=str, dest='format', default="")
    parser.add_argument('--output', '-o', help='Output file name', type=str, dest='output', default="")
    parser.add_argument('--no', '-n', help='Disable automatic exclude mode', action='store_true', dest='disable')
    parser.add_argument('--license', '-l', help='License name to add', type=str, dest='license', default="")
    parser.add_argument('--copyright', '-c', help='Copyright to add', type=str, dest='copyright', default="")
    parser.add_argument('--help', '-h', help='Print help message', action='store_true', dest='help')
    parser.add_argument('--ignore', '-i', help='Do not write log to file', action='store_false', dest='log')
    parser.add_argument('--version', '-v', help='Print FOSSLight Prechecker version', action='store_true', dest='version')
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit:
        print_invalid_msg("illegal option")
        sys.exit(0)

    if unknown:
        print_invalid_msg("illegal option")
        sys.exit(0)

    if args.help:
        print_help_msg()

    if args.version:
        print_package_version(PKG_NAME, "FOSSLight Prechecker Version")
        sys.exit(0)

    if not args.path:
        args.path = os.getcwd()

    if args.mode == "lint":
        run_lint(args.path, args.disable, args.output, args.format, args.log)
    elif args.mode == "convert":
        convert_report(args.path, args.output, args.format, args.log)
    elif args.mode == "add":
        add_content(args.path, args.license, args.copyright, args.output, args.log)
    else:
        print_invalid_msg("illegal mode - choose between a, b, and c")


if __name__ == "__main__":
    main()

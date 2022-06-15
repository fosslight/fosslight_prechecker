#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import argparse
from ._help import print_help_msg
from ._fosslight_reuse import run_lint
from fosslight_oss_pkg.fosslight_oss_pkg import convert_report
from ._add import add_content


def main():
    parser = argparse.ArgumentParser(description='FOSSLight Reuse', prog='fosslight_reuse', add_help=False)
    parser.add_argument('mode', nargs='?', help='lint | convert | add', default="")
    parser.add_argument('--path', '-p', help='Path to check', type=str, dest='path', default="")
    parser.add_argument('--format', '-f', help='Format of ouput', type=str, dest='format', default="")
    parser.add_argument('--output', '-o', help='Output file name', type=str, dest='output', default="")
    parser.add_argument('--no', '-n', help='Disable automatic exclude mode', action='store_true', dest='disable')
    parser.add_argument('--license', '-l', help='License name to add', type=str, dest='license', default="")
    parser.add_argument('--copyright', '-c', help='Copyright to add', type=str, dest='copyright', default="")
    parser.add_argument('--sheet', '-s', help='Sheet name to change to yaml', type=str, dest='sheet', default="")
    parser.add_argument('--help', '-h', help='Print help message', action='store_true', dest='help')
    parser.add_argument('--ignore', '-i', help='Do not write log to file', action='store_false', dest='log')
    try:
        args = parser.parse_args()
    except SystemExit:
        print_help_msg()

    if args.help:
        print_help_msg()

    if args.mode == "lint":
        run_lint(args.path, args.disable, args.output, args.format, args.log)
    elif args.mode == "convert":
        convert_report(args.path, args.output, args.log, args.sheet)
    elif args.mode == "add":
        add_content(args.path, args.license, args.copyright, args.output, args.log)
    else:
        print_help_msg()


if __name__ == "__main__":
    main()

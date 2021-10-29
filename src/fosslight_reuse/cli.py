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
    parser.add_argument('mode', help='lint | convert | add')
    parser.add_argument('--path', '-p', help='Path to check', type=str, dest='path', default="")
    parser.add_argument('--file', '-f', help='Files to check', type=str, dest='file', default="")
    parser.add_argument('--output', '-o', help='Output file name', type=str, dest='output', default="")
    parser.add_argument('--no', '-n', help='Disable automatic exclude mode', action='store_true', dest='disable')
    parser.add_argument('--license', '-l', help='License name to add', type=str, dest='license', default="")
    parser.add_argument('--copyright', '-c', help='Copyright to add', type=str, dest='copyright', default="")
    parser.add_argument('--help', '-h', help='Print help message', action='store_true', dest='help')
    try:
        args = parser.parse_args()
    except SystemExit:
        print_help_msg()

    if args.help:
        print_help_msg()

    if args.mode == "lint":
        run_lint(args.path, args.file, args.disable, args.output)
    elif args.mode == "convert":
        convert_report(args.path, args.file, args.output)
    elif args.mode == "add":
        add_content(args.path, args.file, args.license, args.copyright)
    else:
        pass


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import sys
import os
from fosslight_util.help import print_package_version
from fosslight_oss_pkg._convert import convert_report
from fosslight_prechecker._help import print_help_msg
from fosslight_prechecker._constant import PKG_NAME
from fosslight_prechecker._add import add_content
from fosslight_prechecker._precheck import run_lint


def run_main(mode, path, output, format, no_log, disable, copyright, license, parser):
    if mode != "add" and (copyright != "" or license != ""):
        parser.print_help()
        sys.exit(1)

    if mode == "lint":
        run_lint(path, disable, output, format, no_log)
    elif mode == "add":
        add_content(path, license, copyright, output, no_log)
    elif mode == "convert":
        convert_report(path, output, format, no_log)
    else:
        print("Not supported mode. Select one of 'lint', 'add', or 'convert'")


def main():
    parser = argparse.ArgumentParser(description='FOSSLight Prechecker', prog='fosslight_prechecker', add_help=False)
    parser.add_argument('mode', nargs='?', help='lint(default) | convert | add', choices=['lint', 'add', 'convert'], default='lint')
    parser.add_argument('-h', '--help', help='Print help message', action='store_true', dest='help')
    parser.add_argument('-i', '--ignore', help='Do not write log to file', action='store_false', dest='log')
    parser.add_argument('-v', '--version', help='Print FOSSLight Prechecker version', action='store_true', dest='version')
    parser.add_argument('-n', '--no', help='Disable automatic exclude mode', action='store_true', dest='disable')
    parser.add_argument('-p', '--path', help='Path to check', type=str, dest='path', default="")
    parser.add_argument('-f', '--format', help='Format of ouput', type=str, dest='format', default="")
    parser.add_argument('-o', '--output', help='Output file name', type=str, dest='output', default="")
    parser.add_argument('-l', '--license', help="License name to add(used in only 'add' mode)", type=str, dest='license', default="")
    parser.add_argument('-c', '--copyright', help="Copyright to add(used in only 'add' mode)", type=str, dest='copyright', default="")
    parser.add_argument('--notice', help="Show OSS notice", action='store_true', required=False)
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(0)

    if not args.path:
        args.path = os.getcwd()

    if args.help:
        print_help_msg()
    elif args.version:
        print_package_version(PKG_NAME, "FOSSLight Prechecker Version")
    elif args.notice:
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(__file__)

        data_path = os.path.join(base_path, 'LICENSES')
        print(f"*** {PKG_NAME} open source license notice ***")
        for ff in os.listdir(data_path):
            f = open(os.path.join(data_path, ff), 'r', encoding='utf8')
            print(f.read())
    else:
        run_main(args.mode, args.path, args.output, args.format,
                 args.log, args.disable, args.copyright, args.license, parser)


if __name__ == "__main__":
    main()

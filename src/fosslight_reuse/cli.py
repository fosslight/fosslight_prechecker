#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import argparse
from ._help import _HELP_MESSAGE_REUSE
from ._fosslight_reuse import run_lint
from fosslight_oss_pkg.fosslight_oss_pkg import convert_report


def main():
    parser = argparse.ArgumentParser(description='FOSSLight Reuse', usage=_HELP_MESSAGE_REUSE)
    parser.add_argument('mode', help='lint | report')
    parser.add_argument('--path', '-p', help='Path to check', type=str, dest='path', default="")
    parser.add_argument('--file', '-f', help='Files to check', type=str, dest='file', default="")
    parser.add_argument('--output', '-o', help='Output file name', type=str, dest='output', default="")
    parser.add_argument('--no', '-n', help='Disable automatic exclude mode', action='store_true', dest='disable')
    args = parser.parse_args()

    if args.mode == "lint":
        run_lint(args.path, args.file, args.disable, args.output)
    elif args.mode == "report":
        convert_report(args.path, args.file, args.output)
    else:
        pass


if __name__ == "__main__":
    main()

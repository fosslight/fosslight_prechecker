#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only

PKG_NAME = "fosslight_prechecker"
DEFAULT_EXCLUDE_EXTENSION = ["jar", "png", "exe", "so", "a", "dll", "jpeg", "jpg", "ttf", "lib", "ttc", "pfb",
                             "pfm", "otf", "afm", "dfont", "json"]
OSS_PKG_INFO_FILES = [r"oss-pkg-info[\s\S]*.ya?ml", r"oss-package[\s\S]*.info", r"sbom-info[\s\S]*.ya?ml",
                      "requirement.txt", "requirements.txt", "package.json", "pom.xml", "build.gradle",
                      "podfile.lock", "cartfile.resolved", "pubspec.yaml", "package.resolved", "go.mod",
                      "packages.config", "project.assets.json"]
HTML_RESULT_EXPAND_LIMIT = 10
HTML_RESULT_PRINT_LIMIT = 100

HTML_FORMAT_PREFIX = """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/1999/REC-html401-19991224/strict.dtd">
<html lang="ko">
    <head>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <style>
            .marker{background-color: Yellow;}
            .underline{text-decoration-line: underline;}
            table{width: 100%;}
        </style>
        <title>FOSSLight Prechecker</title>
    </head>
    <body>
            <table cellspacing="0" cellpadding="0" border="0" style="font-family:'arial,sans-serif'">
                <tr>
                    <td>
                        <table cellspacing="0" cellpadding="0" border="0">
                            <tr>
                                <td colspan="3" height="25" style="background:#c00c3f">
                                    <h1 style="margin:0;padding-left:5px;font-size:14px;color:white">FOSSLight Prechecker Lint</h1>
                                </td>
                            </tr>
                            <tr>
                                <td width="1" style="background:#ddd"></td>
                                <td style="padding:40px;">
                                    <div style="padding-bottom:10px;font-size:16px;font-weight:bold;">"""

HTML_COMPLIANCE_SUFFIX = "</div>"
HTML_CELL_HEAD_ROW = """<h2 style="margin:20px 0 0;padding:10px;font-size:16px;">« Files without License or Copyright »</h2>"""
HTML_CELL_PREFIX = """
                                <table cellspacing="0" cellpadding="0" width="100%" border="1" style="font-size:12px;border-color:#ddd;">
                                    <tr>
                                        <th style="padding:5px;background:#f0f0f0;">File</th>
                                        <th style="padding:5px;background:#f0f0f0;">License</th>
                                        <th style="padding:5px;background:#f0f0f0;">Copyright</th>
                                    </tr>"""

HTML_FORMAT_SUFFIX = """
                                    </table>
                                    <br/>
                                </td>
                                <td width="1" style="background:#ddd"></td>
                            </tr>
                            <tr>
                                <td colspan="3" height="1" style="background:#ddd"></td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
    </body>
</html>
"""

HTML_EXPAND_PREFIX = """<details style="font-size:12px;">
                            <summary style="font-size:12px;color:blue;"  class='underline'>Click to expand...</summary>"""

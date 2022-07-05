#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
from reuse import report
from reuse.project import Project
from fosslight_reuse._constant import HTML_FORMAT_PREFIX, HTML_CELL_PREFIX, HTML_FORMAT_SUFFIX, HTML_EXPAND_PREFIX,\
                                      HTML_COMPLIANCE_SUFFIX, HTML_RESULT_PRINT_LIMIT, HTML_RESULT_EXPAND_LIMIT, HTML_CELL_HEAD_ROW


def check_length_of_print_list(input_list: list, list_len: int):
    print_cnt = 0
    print_str = ""
    if not input_list:
        print_str = 'N/A'
    else:
        if list_len <= HTML_RESULT_EXPAND_LIMIT:
            for file in input_list:
                print_str += f"<br>&nbsp;&nbsp;&nbsp; &#183;	{file}"
        elif HTML_RESULT_EXPAND_LIMIT < list_len:
            print_str = HTML_EXPAND_PREFIX
            for file in input_list:
                print_str += f"<br>&nbsp;&nbsp;&nbsp; &#183;	{file}"
                print_cnt += 1
                if print_cnt >= HTML_RESULT_PRINT_LIMIT:
                    print_str += "<br><b>&nbsp;&nbsp;&nbsp; See the log file for more listings...</b>"
                    break
            print_str += "</details>"
    return print_str


def get_html_summary(result_item):
    pkg_file_str = check_length_of_print_list(result_item._oss_pkg_files, len(result_item._oss_pkg_files))
    detected_lic_str = check_length_of_print_list(result_item._detected_licenses, len(result_item._detected_licenses))

    html_lint_str = f"""
    <p style="font-size:14px;line-height:1.2;">
    - Open Source Package file: {pkg_file_str}<br>
    - Detected licenses: {detected_lic_str}<br>
    - Files without copyright / total: {result_item._count_without_cop} / {result_item._count_total_files}<br>
    - Files without license / total: {result_item._count_without_lic} / {result_item._count_total_files}<br></p>
    """
    return html_lint_str


def get_html_compliance(result_item):
    return f"Compliant: {result_item.compliant_result}{HTML_COMPLIANCE_SUFFIX}"


def get_num_of_not_compliant(result_item):
    return int(result_item._count_without_lic) + int(result_item._count_without_cop)


def get_file_report(project, path_to_find, file):
    file_abs_path = os.path.abspath(os.path.join(path_to_find, file))
    file_rep = report.FileReport.generate(project, file_abs_path)
    return file_rep


def get_html_cell(result_item, project: Project, path_to_find):
    cell_str = ""
    for both_file in result_item._files_without_both:
        cell_str += f"""<tr>
                        <td style="padding:5px;">{both_file}</td>
                        <td style="padding:5px;"></td>
                        <td style="padding:5px;"></td>
                    </tr>"""

    for file in result_item._files_without_lic:
        file_rep = get_file_report(project, path_to_find, file)
        cop_text = file_rep.spdxfile.copyright.replace("SPDX-FileCopyrightText: ", "")
        cell_str += f"""<tr>
                        <td style="padding:5px;">{file}</td>
                        <td style="padding:5px;"></td>
                        <td style="padding:5px;">{cop_text}</td>
                    </tr>"""

    for file in result_item._files_without_cop:
        file_rep = get_file_report(project, path_to_find, file)
        lic_in_file = ', '.join(file_rep.spdxfile.licenses_in_file)
        cell_str += f"""<tr>
                        <td style="padding:5px;">{file}</td>
                        <td style="padding:5px;">{lic_in_file}</td>
                        <td style="padding:5px;"></td>
                    </tr>"""
    return cell_str


def result_for_html(result_item, project: Project, path_to_find):
    compliance_str = get_html_compliance(result_item)
    summary_str = get_html_summary(result_item)
    cell_contents_str = ""

    if get_num_of_not_compliant(result_item) <= HTML_RESULT_PRINT_LIMIT:
        cell_contents_str = get_html_cell(result_item, project, path_to_find)
        if result_item._compliant_result == 'OK':
            html_in_str = f"{HTML_FORMAT_PREFIX}{compliance_str}{summary_str}{cell_contents_str}{HTML_FORMAT_SUFFIX}"
        else:
            html_in_str = f"{HTML_FORMAT_PREFIX}{compliance_str}{summary_str}{HTML_CELL_HEAD_ROW}{HTML_CELL_PREFIX}\
                            {cell_contents_str}{HTML_FORMAT_SUFFIX}"
    else:
        cell_contents_str = "There are so many incompliant files. See the log file for more listings...</br>"
        html_in_str = f"{HTML_FORMAT_PREFIX}{compliance_str}{summary_str}{HTML_CELL_HEAD_ROW}{cell_contents_str}{HTML_FORMAT_SUFFIX}"

    if result_item.execution_error:
        err_str = ""
        execution_err_str = "<b> &#9888; Execution Error </b>"
        for error in result_item.execution_error:
            err_str = f"<br>&nbsp;&nbsp;&nbsp; - {error}"
            execution_err_str += err_str
        html_in_str = f"{HTML_FORMAT_PREFIX}{compliance_str}{summary_str}{execution_err_str}{HTML_FORMAT_SUFFIX}"

    return html_in_str

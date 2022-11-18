#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import io
import sys
import platform
import yaml
import fnmatch
import xml.etree.ElementTree as ET
import logging
import fosslight_util.constant as constant
import re
from pathlib import Path
from reuse.project import Project
from fosslight_prechecker._result_html import result_for_html
from fosslight_util.parsing_yaml import find_sbom_yaml_files, parsing_yml
from fosslight_util.output_format import check_output_format


CUSTOMIZED_FORMAT_FOR_PRECHECKER = {'html': '.html', 'xml': '.xml', 'yaml': '.yaml'}
RULE_LINK = "https://oss.lge.com/guide/process/osc_process/1-identification/copyright_license_rule.html"
MSG_REFERENCE = "Ref. Copyright and License Writing Rules in Source Code. : " + RULE_LINK
MSG_FOLLOW_LIC_TXT = "Follow the Copyright and License Writing Rules in Source Code. : " + RULE_LINK
EX_IOERR = 74
logger = logging.getLogger(constant.LOGGER_NAME)
is_windows = platform.system() == 'Windows'


class ResultItem:
    def __init__(self):
        self._compliant_result = ""
        self._summary = ""
        self._oss_pkg_files = []
        self._detected_licenses = []
        self._count_total_files = ""
        self._count_without_both = ""
        self._count_without_lic = ""
        self._count_without_cop = ""
        self._files_without_both = []
        self._files_without_lic = []
        self._files_without_cop = []
        self._os_info = ""
        self._path_to_analyze = ""
        self._python_ver = ""
        self._fl_prechecker_ver = ""
        self._log_msg = ""
        self._check_only_file_mode = False
        self.execution_error = []

    @property
    def compliant_result(self):
        return self._compliant_result

    @compliant_result.setter
    def compliant_result(self, value):
        if value:
            self._compliant_result = "OK"
        else:
            self._compliant_result = "Not-OK"

    @property
    def oss_pkg_files(self):
        return self._oss_pkg_files

    def get_print_yaml(self):
        result_item = {}
        result_item["Compliant"] = self._compliant_result
        result_summary_item = {}
        result_summary_item["Open Source Package File"] = is_list_empty(self._oss_pkg_files)
        result_summary_item["Detected Licenses"] = is_list_empty(self._detected_licenses)
        result_summary_item["Files without license / total"] = f"{self._count_without_lic} / {self._count_total_files}"
        result_summary_item["Files without copyright / total"] = f"{self._count_without_cop} / {self._count_total_files}"

        result_item["Summary"] = result_summary_item
        result_item["Files without license and copyright"] = is_list_empty(self._files_without_both)
        result_item["Files without license"] = is_list_empty(self._files_without_lic)
        result_item["Files without copyright"] = is_list_empty(self._files_without_cop)

        result_tool_item = {}
        result_tool_item["OS"] = self._os_info
        result_tool_item["Analyze path"] = self._path_to_analyze
        result_tool_item["Python version"] = self._python_ver
        result_tool_item["fosslight_prechecker version"] = self._fl_prechecker_ver
        result_item["Tool Info"] = result_tool_item
        if self.execution_error:
            result_item["Execution Error"] = self.execution_error
        root_item = {"Checking copyright/license writing rules": result_item}
        return root_item


def is_list_empty(list: list):
    if list:
        return list
    else:
        return "N/A"


def result_for_xml(result_item: ResultItem):
    str_xml_result = ""
    _root_xml_item = ET.Element('results')

    if result_item.compliant_result != "OK":
        if not result_item._check_only_file_mode:
            _SUMMARY_PREFIX = "\n# SUMMARY\n"
            str_xml_result = f"* Open Source Package File: {', '.join(result_item._oss_pkg_files)}\n \
                               * Detected Licenses : {', '.join(result_item._detected_licenses)}\n \
                               * Files without copyright : {result_item._count_without_cop} / {result_item._count_total_files}\n \
                               * Files without license : {result_item._count_without_lic} / {result_item._count_total_files}\n"

            _SUMMARY_SUFFIX = '\n\n' + MSG_REFERENCE
            str_summary = f"{_SUMMARY_PREFIX}{str_xml_result}{_SUMMARY_SUFFIX}"
            items = ET.Element('error')
            items.set('id', 'rule_key_osc_checker_01')
            items.set('line', '0')
            items.set('msg', str_summary)
            _root_xml_item.append(items)
        else:
            for file_name in (set(result_item._files_without_lic) | set(result_item._files_without_cop)):
                items = ET.Element('error')
                items.set('file', file_name)
                items.set('id', 'rule_key_osc_checker_02')
                items.set('line', '0')
                items.set('msg', MSG_FOLLOW_LIC_TXT)
                _root_xml_item.append(items)

            for file_name in result_item._files_without_cop:
                items = ET.Element('error')
                items.set('file', file_name)
                items.set('id', 'rule_key_osc_checker_02')
                items.set('line', '0')
                items.set('msg', MSG_FOLLOW_LIC_TXT)
                _root_xml_item.append(items)

    if result_item.execution_error:
        error_xml = ET.Element('execution_errors')
        for error in result_item.execution_error:
            error_xml_sub = ET.SubElement(error_xml, 'execution_error')
            error_xml_sub.text = error
        _root_xml_item.append(error_xml)
    return _root_xml_item


def write_result_xml(result_file: str, exit_code: int, result_item: ResultItem, _result_log: str):
    success = False
    # Create a new XML file with the results
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        _root_xml_item = result_for_xml(result_item)
        ET.ElementTree(_root_xml_item).write(result_file, encoding="UTF-8", xml_declaration=True)
        success = True
    except Exception as ex:
        logger.error(f"Error_to_write_xml: {ex}")
        exit_code = EX_IOERR
    return success, exit_code


def write_result_html(result_file: str, exit_code: int, result_item: ResultItem, project: Project, path_to_find):
    success = False
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        html_result = result_for_html(result_item, project, path_to_find)
        with open(result_file, 'w') as f:
            f.write(html_result)
        success = True
    except Exception as ex:
        logger.error(f"Error_to_write_html: {ex}")
        exit_code = EX_IOERR
    return success, exit_code


def write_result_yaml(result_file: str, exit_code: int, result_item: ResultItem):
    success = False
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        yaml_result = result_item.get_print_yaml()
        # Make yaml file
        with io.open(result_file, 'w', encoding='utf8') as outfile:
            yaml.dump(yaml_result, outfile, default_flow_style=False, sort_keys=False, allow_unicode=True)
        success = True
    except Exception as ex:
        logger.error(f"Error_to_write_yaml: {ex}")
        exit_code = EX_IOERR
    return success, exit_code


def create_result_file(output_file_name, format='', _start_time=""):
    success, msg, output_path, output_file, output_extension = check_output_format(output_file_name, format, CUSTOMIZED_FORMAT_FOR_PRECHECKER)
    if success:
        result_file = ""
        if output_path == "":
            output_path = os.getcwd()
        else:
            output_path = os.path.abspath(output_path)

        if output_file != "":
            result_file = f"{output_file}{output_extension}"
        else:
            if output_extension == '.yaml' or output_extension == "":
                result_file = f"fosslight_lint_{_start_time}.yaml"
            elif output_extension == '.html':
                result_file = f"fosslight_lint_{_start_time}.html"
            elif output_extension == '.xml':
                result_file = f"fosslight_lint_{_start_time}.xml"
            else:
                logger.error("Not supported file extension")

        result_file = os.path.join(output_path, result_file)
    else:
        logger.error(f"Format error - {msg}")
        sys.exit(1)

    return result_file, output_path, output_extension


def get_path_in_yaml(oss_item):
    path_in_yaml = [os.path.join(oss_item.relative_path, file) for file in oss_item.source_name_or_path]
    if is_windows:
        path_in_yaml = [path.replace(os.sep, '/') for path in path_in_yaml]
    return path_in_yaml


def extract_files_in_path(remove_file_list, base_file_list, return_found=False):
    extract_files = []
    remained_file_to_remove = []
    remained_base_files = []

    if base_file_list:
        intersection_files = list(set(base_file_list) & set(remove_file_list))
        extract_files.extend(intersection_files)
        remained_base_files = list(set(base_file_list) - set(intersection_files))
        remained_file_to_remove = list(set(remove_file_list) - set(intersection_files))

    for remove_pattern in remained_file_to_remove:
        for file in remained_base_files[:]:
            if fnmatch.fnmatch(file, remove_pattern) or re.search(remove_pattern, file):
                extract_files.append(file)
                remained_base_files.remove(file)
    return extract_files if return_found else remained_base_files


def exclude_file_in_yaml(path_to_find, yaml_files, license_missing_files, copyright_missing_files):
    excluded_path = []
    lic_present_path = []
    cop_present_path = []
    for file in yaml_files:
        oss_items, _ = parsing_yml(file, path_to_find)
        for oss_item in oss_items:
            if oss_item.exclude:
                excluded_path.extend(get_path_in_yaml(oss_item))
            else:
                if oss_item.license:
                    lic_present_path.extend(get_path_in_yaml(oss_item))
                if oss_item.copyright:
                    cop_present_path.extend(get_path_in_yaml(oss_item))

    total_missing_files = list(license_missing_files.union(copyright_missing_files))
    files_with_exclude_removed = extract_files_in_path(excluded_path, total_missing_files, True)
    license_missing_files = extract_files_in_path(lic_present_path, list(license_missing_files - set(files_with_exclude_removed)))
    copyright_missing_files = extract_files_in_path(cop_present_path, list(copyright_missing_files - set(files_with_exclude_removed)))

    return license_missing_files, copyright_missing_files


def result_for_summary(path_to_find, oss_pkg_info_files, license_missing_files, copyright_missing_files,
                       prj_report, _result_log, _check_only_file_mode, file_to_check_list, error_items, exclude_files):
    prechecker_compliant = False
    detected_lic = []
    missing_both_files = []
    file_total_num = ""
    total_files_exclude = ()

    if _check_only_file_mode:
        file_total_num = len(file_to_check_list)
    else:
        if not path_to_find.endswith('/'):
            path_to_find += '/'
        total_files = [str(file_report.path).replace(path_to_find, '', 1) for file_report in prj_report.file_reports]
        total_files_exclude = set(total_files) - set(exclude_files)
        file_total_num = len(total_files_exclude)

        # Get detected License
        for i, lic in enumerate(sorted(prj_report.used_licenses)):
            detected_lic.append(lic)

    if oss_pkg_info_files:
        oss_yaml_files = find_sbom_yaml_files(path_to_find)
        # Exclude files in yaml
        license_missing_files, copyright_missing_files = exclude_file_in_yaml(path_to_find, oss_yaml_files,
                                                                              set(license_missing_files) - set(oss_pkg_info_files),
                                                                              set(copyright_missing_files) - set(oss_pkg_info_files))
        # Subtract excluded files(untracked or ignored file)
        oss_pkg_info_files = list(set(oss_pkg_info_files) - set(exclude_files))

    if len(license_missing_files) == 0 and len(copyright_missing_files) == 0:
        prechecker_compliant = True

    # Remove duplicated file
    missing_both_files = list(set(license_missing_files) & set(copyright_missing_files))
    license_missing_files = list(set(license_missing_files) - set(missing_both_files))
    copyright_missing_files = list(set(copyright_missing_files) - set(missing_both_files))

    # Save result items
    result_item = ResultItem()
    result_item.compliant_result = prechecker_compliant
    result_item._oss_pkg_files = oss_pkg_info_files
    result_item._detected_licenses = detected_lic
    result_item._count_total_files = file_total_num
    result_item._count_without_both = str(len(missing_both_files))
    result_item._count_without_lic = str(len(license_missing_files) + len(missing_both_files))
    result_item._count_without_cop = str(len(copyright_missing_files) + len(missing_both_files))
    result_item._files_without_both = sorted(missing_both_files)
    result_item._files_without_lic = sorted(license_missing_files)
    result_item._files_without_cop = sorted(copyright_missing_files)
    result_item._fl_prechecker_ver = _result_log["Tool Info"]
    result_item._path_to_analyze = _result_log["Path to analyze"]
    result_item._os_info = _result_log["OS"]
    result_item._python_ver = _result_log["Python version"]
    result_item._check_only_file_mode = _check_only_file_mode
    result_item.execution_error = error_items
    return result_item


def write_result_file(result_file, output_extension, exit_code, result_item, _result_log, project, path_to_find):
    success = False
    if output_extension == ".yaml" or output_extension == "":
        success, exit_code = write_result_yaml(result_file, exit_code, result_item)
    elif output_extension == ".html":
        success, exit_code = write_result_html(result_file, exit_code, result_item, project, path_to_find)
    elif output_extension == ".xml":
        success, exit_code = write_result_xml(result_file, exit_code, result_item, _result_log)
    else:
        logger.info("Not supported file extension")

    if success:
        # Print yaml result
        yaml_result = result_item.get_print_yaml()
        str_yaml_result = yaml.safe_dump(yaml_result, allow_unicode=True, sort_keys=False)
        logger.info(str_yaml_result)
    return success, exit_code

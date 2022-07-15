#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import io
import sys
import yaml
import fnmatch
import xml.etree.ElementTree as ET
import logging
import fosslight_util.constant as constant
from pathlib import Path
from reuse.project import Project
from fosslight_reuse._result_html import result_for_html
from fosslight_util.parsing_yaml import find_all_oss_pkg_files, parsing_yml
from fosslight_util.output_format import check_output_format


CUSTOMIZED_FORMAT_FOR_REUSE = {'html': '.html', 'xml': '.xml', 'yaml': '.yaml'}
RULE_LINK = "https://oss.lge.com/guide/process/osc_process/1-identification/copyright_license_rule.html"
MSG_REFERENCE = "Ref. Copyright and License Writing Rules in Source Code. : " + RULE_LINK
MSG_FOLLOW_LIC_TXT = "Follow the Copyright and License Writing Rules in Source Code. : " + RULE_LINK
FNMATCH_SPECIAL_CHARACTERS = ['*', '?', '[']

logger = logging.getLogger(constant.LOGGER_NAME)


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
        self._fl_reuse_ver = ""
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
        result_tool_item["fosslight_reuse version"] = self._fl_reuse_ver
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
        exit_code = os.EX_IOERR
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
        exit_code = os.EX_IOERR
    return success, exit_code


def write_result_yaml(result_file: str, exit_code: int, result_item: ResultItem):
    success = False
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        yaml_result = result_item.get_print_yaml()
        # Make yaml file
        with io.open(result_file, 'w', encoding='utf8') as outfile:
            yaml.dump(yaml_result, outfile, default_flow_style=False, sort_keys=False)
        success = True
    except Exception as ex:
        logger.error(f"Error_to_write_yaml: {ex}")
        exit_code = os.EX_IOERR
    return success, exit_code


def create_result_file(output_file_name, format='', _start_time=""):
    success, msg, output_path, output_file, output_extension = check_output_format(output_file_name, format, CUSTOMIZED_FORMAT_FOR_REUSE)
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
                result_file = f"FOSSLight_Reuse_{_start_time}.yaml"
            elif output_extension == '.html':
                result_file = f"FOSSLight_Reuse_{_start_time}.html"
            elif output_extension == '.xml':
                result_file = f"FOSSLight_Reuse_{_start_time}.xml"
            else:
                logger.error("Not supported file extension")

        result_file = os.path.join(output_path, result_file)
    else:
        logger.error(f"Format error - {msg}")
        sys.exit(1)

    return result_file, output_path, output_extension


def get_only_pkg_info_yaml_file(pkg_info_files):
    for yaml_file in pkg_info_files:
        abs_path = os.path.join(os.getcwd(), yaml_file)
        if os.path.basename(abs_path) == "oss-pkg-info.yaml":
            yield yaml_file


def get_path_in_yaml(oss_item):
    for source_name_or_path in oss_item.source_name_or_path:
        yield os.path.join(oss_item.relative_path, source_name_or_path)


def get_diff_list(setA, setB):
    return list(set(setA) - set(setB))


def extract_files_in_path(path_to_find, filepath, input_list):
    extract_files = []
    remained_files = input_list
    remained_path = filepath
    intersection_files = []
    dir_files = []
    dir_files_path = []

    if not path_to_find.endswith("/"):
        path_to_find += "/"
    filepath_rel = [file.replace(path_to_find, '') for file in filepath]

    if input_list:
        for path in filepath_rel:
            if os.path.isdir(os.path.join(path_to_find, path)):
                dir_files = os.listdir(os.path.join(path_to_find, path))
                dir_files_path = [os.path.join(path, file) for file in dir_files]
                extract_files.extend(dir_files_path)
                remained_files = get_diff_list(remained_files, intersection_files)
                remained_path = get_diff_list(remained_path, intersection_files)
            else:
                intersection_files = list(set(remained_files) & set(filepath_rel))
                extract_files.extend(intersection_files)
                remained_files = get_diff_list(remained_files, intersection_files)
                remained_path = get_diff_list(remained_path, intersection_files)

        for file in remained_files:
            for path in remained_path:
                if fnmatch.fnmatch(file, path):
                    extract_files.append(file)
    return extract_files


def exclude_path_in_yaml(path_to_find, yaml_files, license_missing_files, copyright_missing_files):
    excluded_path = []
    excluded_list = []
    lic_present_path = []
    lic_present_list = []
    cop_present_path = []
    cop_present_list = []
    total_missing_list = set(license_missing_files + copyright_missing_files)

    for file in yaml_files:
        oss_items, _ = parsing_yml(file, path_to_find)
        for oss_item in oss_items:
            if oss_item.exclude:
                excluded_path = list(get_path_in_yaml(oss_item))
                excluded_list.extend(extract_files_in_path(path_to_find, excluded_path, total_missing_list))
                license_missing_files = get_diff_list(license_missing_files, excluded_list)
                copyright_missing_files = get_diff_list(copyright_missing_files, excluded_list)
            if oss_item.license:
                lic_present_path = list(get_path_in_yaml(oss_item))
                lic_present_list = extract_files_in_path(path_to_find, lic_present_path, license_missing_files)
                license_missing_files = get_diff_list(license_missing_files, lic_present_list)
            if oss_item.copyright:
                cop_present_path = list(get_path_in_yaml(oss_item))
                cop_present_list = extract_files_in_path(path_to_find, cop_present_path, copyright_missing_files)
                copyright_missing_files = get_diff_list(copyright_missing_files, cop_present_list)
    return license_missing_files, copyright_missing_files


def result_for_summary(path_to_find, oss_pkg_info_files, license_missing_files, copyright_missing_files,
                       prj_report, _result_log, _check_only_file_mode, file_to_check_list, error_items):
    reuse_compliant = False
    detected_lic = []
    missing_both_files = []
    file_total = ""

    if _check_only_file_mode:
        file_total = len(file_to_check_list)
    else:
        file_total = len(prj_report.file_reports)
        # Get detected License
        for i, lic in enumerate(sorted(prj_report.used_licenses)):
            detected_lic.append(lic)

    if oss_pkg_info_files:
        pkg_info_yaml_files = find_all_oss_pkg_files(path_to_find, oss_pkg_info_files)
        yaml_file = get_only_pkg_info_yaml_file(pkg_info_yaml_files)
        # Get path to be excluded in yaml file
        license_missing_files, copyright_missing_files = exclude_path_in_yaml(path_to_find, yaml_file,
                                                                              license_missing_files,
                                                                              copyright_missing_files)

    # Subtract license or copyright presenting file and excluded file
    license_missing_files = list(set(license_missing_files) - set(oss_pkg_info_files))
    copyright_missing_files = list(set(copyright_missing_files) - set(oss_pkg_info_files))

    if len(license_missing_files) == 0 and len(copyright_missing_files) == 0:
        reuse_compliant = True

    # Remove duplicated file
    missing_both_files = list(set(license_missing_files) & set(copyright_missing_files))
    license_missing_files = list(set(license_missing_files) - set(missing_both_files))
    copyright_missing_files = list(set(copyright_missing_files) - set(missing_both_files))

    # Save result items
    result_item = ResultItem()
    result_item.compliant_result = reuse_compliant
    result_item._oss_pkg_files = oss_pkg_info_files
    result_item._detected_licenses = detected_lic
    result_item._count_total_files = file_total
    result_item._count_without_both = str(len(missing_both_files))
    result_item._count_without_lic = str(len(license_missing_files) + len(missing_both_files))
    result_item._count_without_cop = str(len(copyright_missing_files) + len(missing_both_files))
    result_item._files_without_both = sorted(missing_both_files)
    result_item._files_without_lic = sorted(license_missing_files)
    result_item._files_without_cop = sorted(copyright_missing_files)
    result_item._fl_reuse_ver = _result_log["Tool Info"]
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import io
import sys
import yaml
import xml.etree.ElementTree as ET
import logging
import fosslight_util.constant as constant
from fosslight_util.output_format import check_output_format
from yaml import safe_dump
from pathlib import Path

_CUSTOMIZED_FORMAT_FOR_REUSE = {'html': '.html', 'xml': '.xml', 'yaml': '.yaml'}

logger = logging.getLogger(constant.LOGGER_NAME)
_root_xml_item = ET.Element('results')


class ResultItem:
    def __init__(self):
        self._compliant_result = ""
        self._summary = ""
        self._oss_pkg_files = []
        self._detected_licenses = []
        self._count_total_files = ""
        self._count_without_lic = ""
        self._count_without_cop = ""
        self._files_without_both = []
        self._files_without_lic = []
        self._files_without_cop = []
        self._os_info = ""
        self._path_to_analyze = ""
        self._python_ver = ""
        self._fl_reuse_ver = ""

    @property
    def compliant_result(self):
        return self._compliant_result

    @compliant_result.setter
    def compliant_result(self, value):
        if value:
            self._compliant_result = "OK"
        else:
            self._compliant_result = "Not OK"

    @property
    def oss_pkg_files(self):
        return self._oss_pkg_files

    @oss_pkg_files.setter
    def oss_pkg_files(self, file):
        if not file:
            self._oss_pkg_files = "N/A"
        else:
            self._oss_pkg_files = file

    @property
    def detected_licenses(self):
        return self._detected_licenses

    @detected_licenses.setter
    def detected_licenses(self, lic):
        if not lic:
            self._detected_licenses = "N/A"
        else:
            self._detected_licenses = lic

    @property
    def files_without_both(self):
        return self._files_without_both

    @files_without_both.setter
    def files_without_both(self, file):
        if not file:
            self._files_without_both = "N/A"
        else:
            self._files_without_both = file

    @property
    def files_without_lic(self):
        return self._files_without_lic

    @files_without_lic.setter
    def files_without_lic(self, file):
        if not file:
            self._files_without_lic = "N/A"
        else:
            self._files_without_lic = file

    @property
    def files_without_cop(self):
        return self._files_without_cop

    @files_without_cop.setter
    def files_without_cop(self, file):
        if not file:
            self._files_without_cop = "N/A"
        else:
            self._files_without_cop = file

    def get_print_yaml(self):
        result_item = {}
        result_item["Compliant"] = self._compliant_result
        result_summary_item = {}
        result_summary_item["Open Source Package File"] = self.oss_pkg_files
        result_summary_item["Detected Licenses"] = self.detected_licenses
        result_summary_item["Count without license / Total"] = f"{self._count_without_lic} / {self._count_total_files}"
        result_summary_item["Count without copyright / Total"] = f"{self._count_without_cop} / {self._count_total_files}"

        result_item["Summary"] = result_summary_item
        result_item["Files without license and copyright"] = self.files_without_both
        result_item["Files without license"] = self.files_without_lic
        result_item["Files without copyright"] = self.files_without_cop

        result_tool_item = {}
        result_tool_item["OS Info"] = self._os_info
        result_tool_item["Path to analyze"] = self._path_to_analyze
        result_tool_item["Python Version"] = self._python_ver
        result_tool_item["FL Reuse Version"] = self._fl_reuse_ver
        result_item["Tool Info"] = result_tool_item

        root_item = {"Checking copyright/license writing rules": result_item}
        return root_item


def write_result_xml(result_file: str, exit_code: int, _result_log: str) -> None:
    success = False
    # Create a new XML file with the results
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        ET.ElementTree(_root_xml_item).write(result_file, encoding="UTF-8", xml_declaration=True)
        error_items = ET.ElementTree(_root_xml_item).findall('system_error')
        if len(error_items) > 0:
            logger.warning("# SYSTEM ERRORS")
            for xml_item in error_items:
                logger.warning(xml_item.text)
    except Exception as ex:
        logger.error(f"Error_to_write_xml: {ex}")
        exit_code = os.EX_IOERR
    try:
        _str_final_result_log = safe_dump(_result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
        success = True
    except Exception as ex:
        logger.warning(f"Failed to print result log. {ex}")
    return success, exit_code


def write_result_html(result_file: str, exit_code: int, _result_log: str) -> None:
    success = False
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        success = True
    except Exception as ex:
        logger.error(f"Error_to_write_html: {ex}")
        exit_code = os.EX_IOERR
    return success, exit_code


def write_result_yaml(result_file: str, exit_code: int, result_item: ResultItem) -> None:
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


def create_result_file(output_file_name, format, _start_time=""):
    success, msg, output_path, output_file, output_extension = check_output_format(output_file_name, format, _CUSTOMIZED_FORMAT_FOR_REUSE)
    if success:
        result_file = ""
        if output_path == "":
            output_path = os.getcwd()
        else:
            output_path = os.path.abspath(output_path)

        if output_file != "":
            result_file = f"{output_file}.{format}"
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

    return result_file


def write_result_file(result_file, format, exit_code, result_item, _result_log):
    success = False
    if format == "" or format == "yaml":
        success, exit_code = write_result_yaml(result_file, exit_code, result_item)
    elif format == "html":
        success, exit_code = write_result_html(result_file, exit_code, _result_log)
    elif format == "xml":
        success, exit_code = write_result_xml(result_file, exit_code, _result_log)
    else:
        logger.info("Not supported file extension")

    if success:
        # Print yaml result
        yaml_result = result_item.get_print_yaml()
        yaml.dump(yaml_result, sys.stdout, default_flow_style=False, sort_keys=False)

    return success, exit_code

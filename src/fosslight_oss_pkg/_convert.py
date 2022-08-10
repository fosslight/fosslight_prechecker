#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import sys
import re
import logging
import platform
from datetime import datetime
from pathlib import Path
from yaml import safe_dump
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.set_log import init_log
from fosslight_util.output_format import check_output_format
from fosslight_util.parsing_yaml import find_sbom_yaml_files
from ._parsing_excel import convert_excel_to_yaml, convert_yml_to_excel

CUSTOMIZED_FORMAT_FOR_PRECHECKER = {'yaml': '.yaml', 'excel': '.xlsx'}
_PKG_NAME = "fosslight_prechecker"
logger = logging.getLogger(LOGGER_NAME)


def find_report_file(path_to_find):
    file_to_find = ["FOSSLight-Report.xlsx", "OSS-Report.xlsx"]

    try:
        for file in file_to_find:
            file_with_path = os.path.join(path_to_find, file)
            if os.path.isfile(file_with_path):
                return file
        for root, dirs, files in os.walk(path_to_find):
            for file in files:
                file_name = file.lower()
                p = re.compile(r"[\s\S]*OSS[\s\S]*-Report[\s\S]*.xlsx", re.I)
                if p.search(file_name):
                    return os.path.join(root, file)
    except Exception as error:
        logger.debug("Find report:"+str(error))
    return ""


def check_extension_and_format(file, format):
    if (file.endswith((".yaml", ".yml")) and format == "yaml") or \
       (file.endswith(".xlsx") and format == "excel"):
        logger.error(f"File extension is not matched with input format({format})")
        sys.exit(1)


def convert_report(base_path, output_name, format, need_log_file=True, sheet_names=""):
    oss_yaml_files = []
    oss_report_files = ""  # TODO: Change to list type for multiple Report files
    file_option_on = False
    convert_yml_mode = False
    convert_excel_mode = False
    output_report = ""
    output_yaml = ""
    now = datetime.now().strftime('%Y%m%d_%H-%M-%S')
    is_window = platform.system() == "Windows"

    success, msg, output_path, output_name, output_extension = check_output_format(output_name, format, CUSTOMIZED_FORMAT_FOR_PRECHECKER)

    logger, _result_log = init_log(os.path.join(output_path, f"fosslight_prechecker_log_{now}.txt"),
                                   need_log_file, logging.INFO, logging.DEBUG, _PKG_NAME, base_path)
    if success:
        if output_path == "":
            output_path = os.getcwd()
        else:
            try:
                Path(output_path).mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        if output_name != "":
            output_report = os.path.join(output_path, output_name)
            output_yaml = os.path.join(output_path, output_name)
        else:
            output_report = os.path.join(os.path.abspath(output_path), f"FOSSLight-Report_{now}")
            output_yaml = os.path.join(os.path.abspath(output_path), f"fosslight-sbom-info_{now}")
    else:
        logger.error(f"Format error - {msg}")
        sys.exit(1)

    if os.path.isdir(base_path):
        oss_yaml_files = find_sbom_yaml_files(base_path)
        if oss_yaml_files:
            convert_yml_mode = True
    else:
        if base_path != "":
            files_to_convert = base_path.split(",")
            for file in files_to_convert:
                check_extension_and_format(file, format)
                if file.endswith(".xlsx"):
                    convert_excel_mode = True
                    oss_report_files = file
                elif file.endswith((".yaml", ".yml")):
                    convert_yml_mode = True
                    file_option_on = True
                    oss_yaml_files.append(file)
                else:
                    logger.error("Not support file name or extension")
                    sys.exit(1)

    if not convert_yml_mode and not convert_excel_mode:
        if is_window:
            convert_yml_mode = True
            oss_report_files = find_report_file(base_path)
            if oss_report_files != "":
                convert_excel_mode = True
        else:
            logger.info("fosslight_prechecker: can't convert anything")
            logger.info("Try 'fosslight_prechecker -h for more information")

    if convert_yml_mode:
        convert_yml_to_excel(oss_yaml_files, output_report, file_option_on, base_path)

    if convert_excel_mode:
        convert_excel_to_yaml(oss_report_files, output_yaml, sheet_names)

    try:
        _str_final_result_log = safe_dump(_result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning("Failed to print result log. " + str(ex))

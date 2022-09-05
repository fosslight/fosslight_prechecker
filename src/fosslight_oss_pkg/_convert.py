#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from yaml import safe_dump
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.set_log import init_log
from fosslight_util.output_format import check_output_format
from fosslight_util.parsing_yaml import find_sbom_yaml_files
from ._parsing_excel import convert_yml_to_excel

CUSTOMIZED_FORMAT_FOR_PRECHECKER = {'excel': '.xlsx'}
_PKG_NAME = "fosslight_prechecker"
logger = logging.getLogger(LOGGER_NAME)


def convert_report(base_path, output_name, format, need_log_file=True):
    oss_yaml_files = []
    file_option_on = False
    output_report = ""
    now = datetime.now().strftime('%y%m%d_%H%M')

    success, msg, output_path, output_name, output_extension = check_output_format(output_name, format, CUSTOMIZED_FORMAT_FOR_PRECHECKER)

    logger, _result_log = init_log(os.path.join(output_path, f"fosslight_log_{now}.txt"),
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
        else:
            output_report = os.path.join(os.path.abspath(output_path), f"fosslight_report_{now}")
    else:
        logger.error(f"Format error - {msg}")
        sys.exit(1)

    if os.path.isdir(base_path):
        oss_yaml_files = find_sbom_yaml_files(base_path)
    else:
        if base_path != "":
            files_to_convert = base_path.split(",")
            file_option_on = True
            for file in files_to_convert:
                if os.path.isfile(file):
                    if file.endswith((".yaml", ".yml")):
                        oss_yaml_files.append(file)
                    else:
                        logger.error("Not support file name or extension")
                        sys.exit(1)
                else:
                    logger.error(f"Check the path to find: {base_path}")
                    sys.exit(1)

    if oss_yaml_files:
        convert_yml_to_excel(oss_yaml_files, output_report, file_option_on, base_path)
    else:
        logger.info("fosslight_prechecker: can't convert anything")
        logger.info("Try 'fosslight_prechecker -h' for more information")

    try:
        _str_final_result_log = safe_dump(_result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning("Failed to print result log. " + str(ex))

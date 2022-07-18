#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import logging
import os
import yaml
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.parsing_yaml import find_all_oss_pkg_files, parsing_yml
from fosslight_util.write_excel import write_result_to_excel, write_result_to_csv
from fosslight_util.write_yaml import create_yaml_with_ossitem
from fosslight_util.read_excel import read_oss_report

logger = logging.getLogger(LOGGER_NAME)
IDX_CANNOT_FOUND = -1


def convert_yml_to_excel(oss_pkg_files, output_file, file_option_on, base_path, window):
    items_to_print = []
    sheet_list = {}

    if not file_option_on:
        oss_pkg_files = find_all_oss_pkg_files(base_path, oss_pkg_files)
    else:
        oss_pkg_files = [pkg_file for pkg_file in oss_pkg_files if pkg_file.endswith(('.yaml', '.yml'))]

    for oss_pkg_file in oss_pkg_files:
        try:
            if os.path.isfile(oss_pkg_file):
                logger.warning(f"Read data from : {oss_pkg_file}")

                if file_option_on:
                    base_path = os.path.dirname(oss_pkg_file)
                oss_items, _ = parsing_yml(oss_pkg_file, base_path)
                for item in oss_items:
                    items_to_print.extend(item.get_print_array())
        except Exception as ex:
            logger.error(f"Read yaml file: {ex}")

    if not window:
        try:
            sheet_list["SRC_FL_Reuse"] = items_to_print
            write_result_to_csv(f"{output_file}.csv", sheet_list, True)
            logger.warning(f"Output: {output_file}_SRC_FL_Reuse.csv")
        except Exception as ex:
            logger.error(f"Write .xlsx file : {ex}")
    if items_to_print and len(items_to_print) > 0:
        try:
            sheet_list["SRC_FL_Reuse"] = items_to_print
            write_result_to_excel(f"{output_file}.xlsx", sheet_list)
            logger.warning(f"Output: {output_file}.xlsx")
        except Exception as ex:
            logger.error(f"Write .csv file : {ex}")


def convert_excel_to_yaml(oss_report_to_read, output_file, sheet_names=""):
    _file_extension = ".yaml"
    yaml_dict = {}

    if os.path.isfile(oss_report_to_read):
        try:
            items = read_oss_report(oss_report_to_read, sheet_names)
            for item in items:
                yaml_dict = create_yaml_with_ossitem(item, yaml_dict)
            if yaml_dict:
                output_file = output_file if output_file.endswith(_file_extension) else output_file + _file_extension
                write_yaml_file(output_file, yaml_dict)
                logger.warning(f"Output: {output_file}")
        except Exception as error:
            logger.error(f"Convert yaml: {error}")
    else:
        logger.error(f"Can't find a file: {oss_report_to_read}")


def write_yaml_file(output_file, json_output):
    with open(output_file, 'w') as f:
        yaml.dump(json_output, f, sort_keys=False)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only

import xlrd
import logging
import os
import json
import yaml
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.oss_item import OssItem
from fosslight_util.parsing_yaml import find_all_oss_pkg_files, parsing_yml, set_value_switch
from fosslight_util.write_excel import write_result_to_excel, write_result_to_csv
from fosslight_util.write_yaml import create_yaml_with_ossitem

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


def read_oss_report(excel_file, sheet_names=""):
    _oss_report_items = []
    _xl_sheets = []
    SHEET_PREFIX_TO_READ = ["bin", "bom", "src"]
    if sheet_names:
        sheet_name_prefix_math = False
        sheet_name_to_read = sheet_names.split(",")
    else:
        sheet_name_prefix_math = True
        sheet_name_to_read = SHEET_PREFIX_TO_READ

    try:
        logger.info(f"Read data from : {excel_file}")
        xl_workbook = xlrd.open_workbook(excel_file)
        for sheet_name in xl_workbook.sheet_names():
            try:
                sheet_name_lower = sheet_name.lower()
                if any(((sheet_name_prefix_math and sheet_name_lower.startswith(sheet_to_read.lower()))
                       or sheet_name_lower == sheet_to_read.lower())
                       for sheet_to_read in sheet_name_to_read):
                    sheet = xl_workbook.sheet_by_name(sheet_name)
                    if sheet:
                        logger.info(f"Load a sheet: {sheet_name}")
                        _xl_sheets.append(sheet)
            except Exception as error:
                logger.debug(f"Failed to load sheet: {sheet_name} {error}")

        for xl_sheet in _xl_sheets:
            _item_idx = {
                "ID": IDX_CANNOT_FOUND,
                "Source Name or Path": IDX_CANNOT_FOUND,
                "Binary Name": IDX_CANNOT_FOUND,
                "OSS Name": IDX_CANNOT_FOUND,
                "OSS Version": IDX_CANNOT_FOUND,
                "License": IDX_CANNOT_FOUND,
                "Download Location": IDX_CANNOT_FOUND,
                "Homepage": IDX_CANNOT_FOUND,
                "Exclude": IDX_CANNOT_FOUND,
                "Copyright Text": IDX_CANNOT_FOUND,
                "Comment": IDX_CANNOT_FOUND,
                "File Name or Path": IDX_CANNOT_FOUND
            }
            num_cols = xl_sheet.ncols
            num_rows = xl_sheet.nrows
            MAX_FIND_HEADER_COLUMN = 5 if num_rows > 5 else num_rows
            DATA_START_ROW_IDX = 1
            for row_idx in range(0, MAX_FIND_HEADER_COLUMN):
                for col_idx in range(row_idx, num_cols):
                    cell_obj = xl_sheet.cell(row_idx, col_idx)
                    if cell_obj.value in _item_idx:
                        _item_idx[cell_obj.value] = col_idx

                if len([key for key, value in _item_idx.items() if value != IDX_CANNOT_FOUND]) > 3:
                    DATA_START_ROW_IDX = row_idx + 1
                    break

            # Get all values, iterating through rows and columns
            column_keys = json.loads(json.dumps(_item_idx))

            for row_idx in range(DATA_START_ROW_IDX, xl_sheet.nrows):
                item = OssItem("")
                valid_row = True
                load_data_cnt = 0

                for column_key, column_idx in column_keys.items():
                    if column_idx != IDX_CANNOT_FOUND:
                        cell_obj = xl_sheet.cell(row_idx, column_idx)
                        cell_value = cell_obj.value
                        if cell_value != "":
                            if column_key != "ID":
                                if column_key:
                                    column_key = column_key.lower().strip()
                                set_value_switch(item, column_key, cell_value)
                                load_data_cnt += 1
                            else:
                                valid_row = False if cell_value == "-" else True
                if valid_row and load_data_cnt > 0:
                    _oss_report_items.append(item)

    except Exception as error:
        logger.error(f"Parsing a OSS Report: {error}")
    return _oss_report_items

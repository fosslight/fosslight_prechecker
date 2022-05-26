#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only

import xlrd
import logging
import os
import json
import yaml
import csv
import xlsxwriter
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.oss_item import OssItem
from fosslight_util.parsing_yaml import find_all_oss_pkg_files, parsing_yml

logger = logging.getLogger(LOGGER_NAME)
IDX_CANNOT_FOUND = -1
HEADER_ROW = ['ID', 'Source Name or Path', 'OSS Name', 'OSS Version', 'License',
              'Download Location', 'Homepage', 'Copyright Text',
              'License Text', 'Exclude', 'Comment']


def convert_yml_to_excel(oss_pkg_files, output_file, file_option_on, base_path, window):
    items_to_print = [HEADER_ROW]

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
                items_to_print.extend(parsing_yml(oss_pkg_file, base_path)[0])
        except Exception as ex:
            logger.error(f"Read yaml file: {ex}")

    if not window:
        write_result_to_csv(items_to_print, output_file)
    if len(items_to_print) > 1:
        write_result_to_excel(items_to_print, output_file)


def convert_excel_to_yaml(oss_report_to_read, output_file):
    _file_extension = ".yaml"
    _output_json = {}
    _row_to_print = []
    _json_root_key = "Open Source Package"

    if os.path.isfile(oss_report_to_read):
        try:
            logger.warning(f"Read data from : {oss_report_to_read}")
            items = read_oss_report(oss_report_to_read)
            for item in items:
                _row_to_print.append(item.get_print_json())
            if len(_row_to_print) > 0:
                output_file = output_file if output_file.endswith(_file_extension) else output_file + _file_extension
                _output_json[_json_root_key] = _row_to_print
                write_yaml_file(output_file, _output_json)
                logger.warning(f"Output: {output_file}")
        except Exception as error:
            logger.error(f"Convert yaml: {error}")
    else:
        logger.error("Can't find a file :"+oss_report_to_read)


def write_result_to_csv(row_list, output_file):
    _file_extension = ".csv"
    try:
        output_file = output_file if output_file.endswith(_file_extension) else output_file + _file_extension
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerows(row_list)
        logger.warning(f"Output: {output_file}")
    except Exception as ex:
        logger.error(f"Write csv: {ex}")


def write_result_to_excel(list_to_print, output_file):
    _file_extension = ".xlsx"
    try:
        output_file = output_file if output_file.endswith(_file_extension) else output_file + _file_extension
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet("SRC")
        write_result_to_sheet(worksheet, list_to_print)
        workbook.close()
        logger.warning(f"Output: {output_file}")
    except Exception as ex:
        logger.error(f"Write excel: {ex}")


def write_result_to_sheet(worksheet, print_list):
    row = 0  # Start from the first cell.
    for item_to_print in print_list:
        for col_num, value in enumerate(item_to_print):
            worksheet.write(row, col_num, value)
        row += 1


def write_yaml_file(output_file, json_output):
    with open(output_file, 'w') as f:
        yaml.dump(json_output, f, sort_keys=False)


def read_oss_report(excel_file):
    _oss_report_items = []
    _sheet_name_to_read = ["BIN (Android)", "BOM", "BIN(Android)", "BIN (Yocto)", "BIN(Yocto)"]
    _xl_sheets = []

    try:
        # Open the workbook
        xl_workbook = xlrd.open_workbook(excel_file)
        for sheet_name in _sheet_name_to_read:
            try:
                sheet = xl_workbook.sheet_by_name(sheet_name)
                if sheet:
                    logger.info(f"Load a sheet: {sheet_name}")
                    _xl_sheets.append(sheet)
            except Exception as error:
                logger.debug(f"Failed to load sheet: {sheet_name} {error}")

        for xl_sheet in _xl_sheets:
            _item_idx = {
                "ID": IDX_CANNOT_FOUND,
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
                                set_value_switch(item, column_key, cell_value)
                                load_data_cnt += 1
                            else:
                                valid_row = False if cell_value == "-" else True
                if valid_row and load_data_cnt > 0:
                    _oss_report_items.append(item)

    except Exception as error:
        logger.error(f"Parsing a OSS Report: {error}")
    return _oss_report_items


def set_value_switch(oss, key, value):
    if key == 'OSS Name':
        oss.name = value
    elif key == 'OSS Version':
        oss.version = value
    elif key == 'Download Location':
        oss.download_location = value
    elif key == 'License':
        oss.license = value
    elif key == 'Binary Name':
        oss.source_name_or_path = value
    elif key == 'File Name or Path':
        oss.source_name_or_path = value
    elif key == 'Copyright Text':
        oss.copyright = value
    elif key == 'Exclude':
        oss.exclude = value
    elif key == 'Comment':
        oss.comment = value
    elif key == 'Homepage':
        oss.homepage = value

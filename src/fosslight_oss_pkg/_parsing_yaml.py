#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import yaml
import xlsxwriter
import logging
import codecs
import os
import sys
import csv
from fosslight_util.constant import LOGGER_NAME
from ._common import OssItem, invalid

_logger = logging.getLogger(LOGGER_NAME)
_HEADER_ROW = ['ID', 'Source Name or Path', 'OSS Name', 'OSS Version', 'License',
               'Download Location', 'Homepage', 'Copyright Text',
               'License Text', 'Exclude', 'Comment']


def convert_yml_to_excel(oss_pkg_files, output_file, file_option_on, base_path, window):
    items_to_print = [_HEADER_ROW]

    if not file_option_on:
        oss_pkg_files = find_all_oss_pkg_files(base_path, oss_pkg_files)
    else:
        oss_pkg_files = [pkg_file for pkg_file in oss_pkg_files if pkg_file.endswith(('.yaml', '.yml'))]

    for oss_pkg_file in oss_pkg_files:
        try:
            if os.path.isfile(oss_pkg_file):
                _logger.warning("Read data from :" + oss_pkg_file)

                if file_option_on:
                    base_path = os.path.dirname(oss_pkg_file)
                items_to_print.extend(parsing_yml(oss_pkg_file, base_path)[0])
        except Exception as ex:
            _logger.error('Read yaml file:' + str(ex))

    if not window:
        write_result_to_csv(items_to_print, output_file)
    if len(items_to_print) > 1:
        write_result_to_excel(items_to_print, output_file)


def write_result_to_csv(row_list, output_file):
    _file_extension = ".csv"
    try:
        output_file = output_file if output_file.endswith(_file_extension) else output_file + _file_extension
        with open(output_file, 'w', newline='') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerows(row_list)
        _logger.warn("Output: " + output_file)
    except Exception as ex:
        _logger.error('Write csv:' + str(ex))


def write_result_to_excel(list_to_print, output_file):
    _file_extension = ".xlsx"
    try:
        output_file = output_file if output_file.endswith(_file_extension) else output_file + _file_extension
        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet("SRC")
        write_result_to_sheet(worksheet, list_to_print)
        workbook.close()
        _logger.warn("Output: "+output_file)
    except Exception as ex:
        _logger.error('Write excel:' + str(ex))


def write_result_to_sheet(worksheet, print_list):
    row = 0  # Start from the first cell.
    for item_to_print in print_list:
        for col_num, value in enumerate(item_to_print):
            worksheet.write(row, col_num, value)
        row += 1


def parsing_yml(yaml_file, base_path):
    oss_list = []
    license_list = []
    idx = 1
    try:
        path_of_yml = os.path.normpath(os.path.dirname(yaml_file))
        base_path = os.path.normpath(base_path)
        relative_path = ""

        if path_of_yml != base_path:
            relative_path = os.path.relpath(path_of_yml, base_path)

        doc = yaml.safe_load(codecs.open(yaml_file, "r", "utf-8"))
        for root_element in doc:
            oss_items = doc[root_element]
            if oss_items:
                for oss in oss_items:
                    item = OssItem(relative_path)
                    for key, value in oss.items():
                        set_value_switch(item, key, value)
                    items_to_print = item.get_print_array()
                    for item_to_print in items_to_print:
                        item_to_print.insert(0, str(idx))
                    oss_list.extend(items_to_print)
                    license_list.extend(item.licenses)
                    idx += 1
    except yaml.YAMLError as ex:
        _logger.error('Parsing yaml :' + str(ex))
    license_list = set(license_list)
    return oss_list, license_list


def find_all_oss_pkg_files(path_to_find, file_to_find):
    oss_pkg_files = []

    if not os.path.isdir(path_to_find):
        _logger.error("Can't find a path :" + path_to_find)
        sys.exit(os.EX_DATAERR)

    try:
        # oss_pkg_files.extend(glob.glob(path_to_find + '/**/'+file, recursive=True)) #glib is too slow
        for p, d, f in os.walk(path_to_find):
            for file in f:
                file_name = file.lower()
                if file_name in file_to_find or (
                        (file_name.endswith("yml") or file_name.endswith("yaml"))
                        and file_name.startswith("oss-pkg-info")):
                    oss_pkg_files.append(os.path.join(p, file))
    except Exception as ex:
        _logger.debug("Error, find all oss-pkg-info files:" + str(ex))

    return oss_pkg_files


def set_value_switch(oss, key, value):
    switcher = {
        'name': oss.set_name,
        'version': oss.set_version,
        'source': oss.set_source,
        'license': oss.set_licenses,
        'file': oss.set_files,
        'copyright': oss.set_copyright,
        'exclude': oss.set_exclude,
        'comment': oss.set_comment,
        'homepage': oss.set_homepage
    }
    func = switcher.get(key, lambda key: invalid(key))
    func(value)

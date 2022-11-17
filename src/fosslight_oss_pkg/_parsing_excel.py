#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import logging
import os
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.parsing_yaml import parsing_yml
from fosslight_util.output_format import write_output_file

logger = logging.getLogger(LOGGER_NAME)

HEADER_CONTENT = ['ID', 'Source Name or Path', 'OSS Name',
                  'OSS Version', 'License',  'Download Location',
                  'Homepage', 'Copyright Text', 'Exclude',
                  'Comment']
MAX_SHEET_NAME_LEN = 31


def get_sheet_name(yaml_file, sheet_list):
    if len(yaml_file) > MAX_SHEET_NAME_LEN:
        yaml_file = yaml_file[0:MAX_SHEET_NAME_LEN]

    count = 1
    while yaml_file in sheet_list:
        end_idx = MAX_SHEET_NAME_LEN - 1 - len(str(count))
        yaml_file = f"{yaml_file[0:end_idx]}_{count}"
        count += 1
        if end_idx == 0:
            yaml_file = ""
            logger.error("Too many duplicated file names")
            break
    return yaml_file


def convert_yml_to_excel(oss_yaml_files, output_file, file_option_on, base_path):
    sheet_list = {}
    header = {}

    for yaml_file in oss_yaml_files:
        try:
            if os.path.isfile(yaml_file):
                items_to_print = []

                logger.info(f"Read data from : {yaml_file}")

                if file_option_on:
                    base_path = os.path.dirname(yaml_file)
                oss_items, _ = parsing_yml(yaml_file, base_path)
                for item in oss_items:
                    items_to_print.extend(item.get_print_array())
                if not base_path.endswith(f"{os.sep}"):
                    base_path += f"{os.sep}"
                yaml_file = yaml_file.replace(base_path, '')
                yaml_file = yaml_file.replace(os.sep, '_')
                yaml_file_sheet = get_sheet_name(yaml_file, sheet_list)

                if yaml_file_sheet:
                    sheet_list[yaml_file_sheet] = items_to_print
                    header[yaml_file_sheet] = HEADER_CONTENT
        except Exception as ex:
            logger.error(f"Read yaml file: {ex}")

    try:
        success, msg, result_file = write_output_file(output_file, '.xlsx', sheet_list, header)
        if success:
            if result_file:
                logger.warning(f"Output: {result_file}")
            else:
                logger.warning("Nothing is detected to convert so output file is not generated.")
        else:
            logger.error(f"Fail to write excel file : {msg}")
    except Exception as ex:
        logger.error(f"Error to write excel file : {ex}")

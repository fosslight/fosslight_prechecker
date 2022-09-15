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
yaml_file_cnt_dict = {}


_HEADER_CONTENT = ['ID', 'Source Name or Path', 'OSS Name',
                   'OSS Version', 'License',  'Download Location',
                   'Homepage', 'Copyright Text', 'Exclude',
                   'Comment']
_HEADER = {'SRC': _HEADER_CONTENT}


def check_duplicated_file_name(yaml_file):
    is_duplicated = False

    if len(yaml_file) > 31:
        yaml_file = yaml_file[0:31]

    # If duplicated
    if yaml_file in yaml_file_cnt_dict.keys():
        count = yaml_file_cnt_dict.get(yaml_file)

        yaml_file_cnt_dict[yaml_file] = count + 1
        is_duplicated = True
    else:
        yaml_file_cnt_dict[yaml_file] = 1
        is_duplicated = False

    return is_duplicated, yaml_file


def convert_yml_to_excel(oss_yaml_files, output_file, file_option_on, base_path):
    sheet_list = {}

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
                if not base_path.endswith("/"):
                    base_path += "/"
                yaml_file = yaml_file.replace(base_path, '')
                yaml_file_sheet = yaml_file.replace('/', '_')

                duplicated, yaml_file_sheet = check_duplicated_file_name(yaml_file_sheet)
                if duplicated:
                    count = yaml_file_cnt_dict[yaml_file_sheet]
                    if count == 2:
                        sheet_list[f"{yaml_file_sheet[0:29]}_1"] = sheet_list.pop(yaml_file_sheet)

                    if count < 10:
                        yaml_file_sheet = f"{yaml_file_sheet[0:29]}_{count}"
                    elif count >= 10 and count < 100:
                        yaml_file_sheet = f"{yaml_file_sheet[0:28]}_{count}"
                    elif count >= 100 and count < 1000:
                        yaml_file_sheet = f"{yaml_file_sheet[0:27]}_{count}"
                    else:
                        logger.error("Too many duplicated file names")
                sheet_list[f"{yaml_file_sheet}"] = items_to_print
                for sheet in sheet_list:
                    _HEADER[f"{sheet}"] = _HEADER_CONTENT
        except Exception as ex:
            logger.error(f"Read yaml file: {ex}")

    try:
        success, msg, result_file = write_output_file(output_file, '.xlsx', sheet_list, _HEADER)
        if success:
            if result_file:
                logger.warning(f"Output: {result_file}")
            else:
                logger.warning("Nothing is detected to convert so output file is not generated.")
        else:
            logger.error(f"Error to write excel file : {msg}")
    except Exception as ex:
        logger.error(f"Error to write excel file : {ex}")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import logging
import os
from typing import Dict, List
from fosslight_util.constant import LOGGER_NAME
from fosslight_util.parsing_yaml import parsing_yml
from fosslight_util.output_format import write_output_file
from fosslight_util.oss_item import ScannerItem
from fosslight_prechecker._constant import PKG_NAME
from datetime import datetime

logger = logging.getLogger(LOGGER_NAME)

HEADER_CONTENT = ['ID', 'Source Name or Path', 'OSS Name',
                  'OSS Version', 'License',  'Download Location',
                  'Homepage', 'Copyright Text', 'Exclude',
                  'Comment']
MAX_SHEET_NAME_LEN = 31


def get_sheet_name(yaml_file: str, sheet_list: Dict[str, List]) -> str:
    if len(yaml_file) > MAX_SHEET_NAME_LEN:
        yaml_file = yaml_file[0:MAX_SHEET_NAME_LEN]

    count = 1
    while yaml_file in sheet_list.keys():
        end_idx = MAX_SHEET_NAME_LEN - 1 - len(str(count))
        yaml_file = f"{yaml_file[0:end_idx]}_{count}"
        count += 1
        if end_idx == 0:
            yaml_file = ""
            logger.error("Too many duplicated file names")
            break
    return yaml_file


def convert_yml_to_excel(
    oss_yaml_files: List[str],
    output_file: str,
    file_option_on: bool,
    base_path: str
) -> None:
    sheet_list = {}
    start_time = datetime.now().strftime('%y%m%d_%H%M')
    scan_item = ScannerItem(PKG_NAME, start_time)
    scan_item.set_cover_pathinfo(base_path, "")
    for yaml_file in oss_yaml_files:
        try:
            if os.path.isfile(yaml_file):
                items_to_print = []

                logger.info(f"Read data from : {yaml_file}")

                if file_option_on:
                    base_path = os.path.dirname(yaml_file)
                file_items, _, _ = parsing_yml(yaml_file, base_path)
                # if file_items is abnormal(empty or invalid)
                if not file_items:
                    continue

                if not base_path.endswith(f"{os.sep}"):
                    base_path += f"{os.sep}"
                tmp_yaml_file = yaml_file.replace(base_path, '')
                tmp_yaml_file = tmp_yaml_file.replace(os.sep, '_')
                yaml_file_sheet = get_sheet_name(tmp_yaml_file, sheet_list)

                if yaml_file_sheet:
                    scan_item.set_cover_comment(f"Converted file:{yaml_file}")
                    row_items = [HEADER_CONTENT]
                    for file_item in file_items:
                        row_items.extend(file_item.get_print_array())
                    sheet_list[yaml_file_sheet] = row_items
                
        except Exception as ex:
            logger.error(f"Read yaml file: {ex}")

    try:
        scan_item.external_sheets = sheet_list
        success, msg, result_file = write_output_file(output_file, '.xlsx', scan_item)
        if success:
            if result_file:
                logger.warning(f"Output: {result_file}")
            else:
                logger.warning("Nothing is detected to convert so output file is not generated.")
        else:
            logger.error(f"Fail to write excel file : {msg}")
    except Exception as ex:
        logger.error(f"Error to write excel file : {ex}")

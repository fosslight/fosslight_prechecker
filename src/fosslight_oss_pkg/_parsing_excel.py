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


def convert_yml_to_excel(oss_yaml_files, output_file, file_option_on, base_path):
    items_to_print = []
    sheet_list = {}

    for yaml_file in oss_yaml_files:
        try:
            if os.path.isfile(yaml_file):
                logger.info(f"Read data from : {yaml_file}")

                if file_option_on:
                    base_path = os.path.dirname(yaml_file)
                oss_items, _ = parsing_yml(yaml_file, base_path)
                for item in oss_items:
                    items_to_print.extend(item.get_print_array())
        except Exception as ex:
            logger.error(f"Read yaml file: {ex}")

    try:
        sheet_list["SRC_FL_Prechecker"] = items_to_print
        success, msg, result_file = write_output_file(output_file, '.xlsx', sheet_list)
        if success:
            if result_file:
                logger.warning(f"Output: {result_file}")
            else:
                logger.warning("Nothing is detected to convert so output file is not generated.")
        else:
            logger.error(f"Error to write excel file : {msg}")
    except Exception as ex:
        logger.error(f"Error to write excel file : {ex}")

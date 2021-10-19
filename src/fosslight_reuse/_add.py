#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import re
import logging
import fosslight_util.constant as constant
from yaml import safe_dump
from fosslight_util.set_log import init_log
from datetime import datetime
from ._fosslight_reuse import reuse_for_project, reuse_for_files, print_error
from reuse.header import run
from reuse._comment import EXTENSION_COMMENT_STYLE_MAP_LOWERCASE
from reuse._main import parser as reuse_arg_parser

_PKG_NAME = "fosslight_reuse"
_result_log = {}
logger = logging.getLogger(constant.LOGGER_NAME)


def check_file_extension(file_list):
    files_filtered = []

    if file_list != "":
        for file in file_list:
            try:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension == "":
                    logger.warning("Error - can't check file extension : " + file)
                if file_extension in EXTENSION_COMMENT_STYLE_MAP_LOWERCASE:
                    files_filtered.append(file)
            except Exception as ex:
                logger.warning("Error - Unknown error to check file exteion " + ex)

    return files_filtered


def check_license_and_copyright(path_to_find, all_files, missing_license, missing_copyright):
    # Check file extension for each list
    all_files_fitered = check_file_extension(all_files)
    missing_license_filtered = check_file_extension(missing_license)
    missing_copyright_filtered = check_file_extension(missing_copyright)

    skip_files = sorted(list(set(all_files_fitered) - set(missing_license_filtered) - set(missing_copyright_filtered)))
    logger.info("# File list that have both license and copyright : {count} / {total}".format(
            count=len(skip_files),
            total=len(all_files)))

    for file in skip_files:
        file_list = list()
        file_list.append(file)

        unused_lic_list, usused_cop_list, error_occurred, project = reuse_for_files(path_to_find, file_list)

    return missing_license_filtered, missing_copyright_filtered


def convert_to_spdx_format(input_string):
    input_string = input_string.replace(" ", "-")
    input_converted = "LicenseRef-" + input_string
    return input_converted


def check_input_format(input_copyright):
    regex = re.compile(r'Copyright(\s)+(\(c\)\s)?\s*\d{4}(-\d{4})*(\s)+(\S)+')
    check_ok = True

    if regex.match(input_copyright) is None:
        logger.warning(" You have to input with following format - Copyright <year> <name>")
        check_ok = False

    return check_ok


def input_license_while_running():
    input_license = ""

    logger.info("# Select a license to write in the license missing files ")
    select = input("   1.MIT,  2.Apache-2.0,  3.LGE-Proprietary,  4.Manaully Input,  5.Not select now : ")
    if select == '1' or select == 'MIT':
        input_license = 'MIT'
    elif select == '2' or select == 'Apache-2.0':
        input_license = 'Apache-2.0'
    elif select == '3' or select == 'LGE Proprietary License':
        input_license = 'LicenseRef-LGE-Proprietary'
    elif select == '4' or select == 'Manually Input':
        input_license = input("   ## Input your License : ")
    elif select == '5' or select == 'Quit' or select == 'quit':
        logger.info(" Not selected any license to write ")
    return input_license


def input_copyright_while_running():
    input_copyright = ""
    input_copyright = input("# Input Copyright to write in the copyright missing files (ex, Copyright <year> <name>) : ")
    if input_copyright == 'Quit' or input_copyright == 'quit' or input_copyright == 'Q':
        return

    return input_copyright


def set_missing_license_copyright(missing_license_filtered, missing_copyright_filtered, project, path_to_find, license, copyright):
    input_license = None
    input_copyright = None

    try:
        main_parser = reuse_arg_parser()
    except Exception as ex:
        print_error('Error_get_arg_parser :' + str(ex))

    # Print missing license
    if missing_license_filtered is not None and len(missing_license_filtered) > 0:
        missing_license_list = []

        logger.info("# Missing license File(s) ")
        for lic_file in sorted(missing_license_filtered):
            logger.info(f"  * {lic_file}")
            missing_license_list.append(lic_file)

        if license == "" and copyright == "":
            input_license = input_license_while_running()
        else:
            input_license = license

        if input_license != "":
            logger.warning(f"  * Your input license : {input_license}")
            parsed_args = main_parser.parse_args(['addheader', '--license', str(input_license)] + missing_license_list)
            try:
                run(parsed_args, project)
            except Exception as ex:
                print_error('Error_call_run_in_license :' + str(ex))
    else:
        logger.info("# There is no missing license file")

    # Print copyright
    if missing_copyright_filtered is not None and len(missing_copyright_filtered) > 0:
        missing_copyright_list = []

        logger.info("# Missing Copyright File(s) ")
        for cop_file in sorted(missing_copyright_filtered):
            logger.info(f"  * {cop_file}")
            missing_copyright_list.append(cop_file)

        if license == "" and copyright == "":
            input_copyright = input_copyright_while_running()
        else:
            input_copyright = copyright

        if input_copyright != "":
            input_copyright = 'Copyright ' + input_copyright
            input_ok = check_input_format(input_copyright)
            if input_ok is False:
                return
            logger.warning(f"  * Your input Copyright : {input_copyright}")
            parsed_args = main_parser.parse_args(['addheader', '--copyright',
                                                  'SPDX-FileCopyrightText: ' + str(input_copyright),
                                                  '--exclude-year'] + missing_copyright_list)
            try:
                run(parsed_args, project)
            except Exception as ex:
                print_error('Error_call_run_in_copyright :' + str(ex))
    else:
        logger.info("# There is no missing copyright file\n")


def get_allfiles_list(path):
    all_files = []

    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_lower_case = file.lower()
                file_abs_path = os.path.join(root, file_lower_case)
                file_rel_path = os.path.relpath(file_abs_path, path)
                all_files.append(file_rel_path)
    except Exception as ex:
        print_error('Error_Get_AllFiles : ' + str(ex))

    return all_files


def save_result_log():
    try:
        _str_final_result_log = safe_dump(_result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning("Failed to print add result log. " + str(ex))


def add_content(path_to_find, file, input_license="", input_copyright=""):
    global _result_log
    file_to_check_list = []
    _check_only_file_mode = False

    if path_to_find == "":
        path_to_find = os.getcwd()
    else:
        path_to_find = os.path.abspath(path_to_find)
        os.chdir(path_to_find)

    now = datetime.now().strftime('%Y%m%d_%H-%M-%S')
    output_dir = os.getcwd()
    logger, _result_log = init_log(os.path.join(output_dir, "fosslight_reuse_add_log_"+now+".txt"),
                                   True, logging.INFO, logging.DEBUG, _PKG_NAME, path_to_find)

    if file != "":
        file_to_check_list = file.split(',')
        _check_only_file_mode = True

    if _check_only_file_mode:
        main_parser = reuse_arg_parser()
        missing_license_list, missing_copyright_list, error_occurred, project = reuse_for_files(path_to_find, file_to_check_list)

        if missing_license_list is not None and len(missing_license_list) > 0:
            if input_license == "" and input_copyright == "":
                input_license = input_license_while_running()

            if input_license != "":
                logger.warning(f"  * Your input license : {input_license}")
                parsed_args = main_parser.parse_args(['addheader', '--license', str(input_license)] + missing_license_list)
                try:
                    run(parsed_args, project)
                except Exception as ex:
                    print_error('Error_call_run_in_license_file_only :' + str(ex))
        else:
            logger.info("# There is no missing license file")

        if missing_copyright_list is not None and len(missing_copyright_list) > 0:
            if input_license == "" and input_copyright == "":
                input_copyright = input_copyright_while_running()

            if input_copyright != "":
                input_copyright = 'Copyright ' + input_copyright
                logger.warning(f"  * Your input Copyright : {input_copyright}")
                parsed_args = main_parser.parse_args(['addheader', '--copyright',
                                                      'SPDX-FileCopyrightText: ' + str(input_copyright),
                                                      '--exclude-year'] + missing_copyright_list)
            try:
                run(parsed_args, project)
            except Exception as ex:
                print_error('Error_call_run_in_copyright_file_only :' + str(ex))
        else:
            logger.info("# There is no missing copyright file\n")
    else:
        # Get all files List in path
        all_files_list = get_allfiles_list(path_to_find)

        str_lint_result, missing_license, missing_copyright, oss_pkg_info, error_occurred, project = reuse_for_project(path_to_find)

        # Print Skipped Files
        missing_license_filtered, missing_copyright_filtered = \
            check_license_and_copyright(path_to_find, all_files_list, missing_license, missing_copyright)

        # Set missing license and copyright
        set_missing_license_copyright(missing_license_filtered,
                                      missing_copyright_filtered,
                                      project,
                                      path_to_find,
                                      input_license,
                                      input_copyright)

    save_result_log()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import re
import logging
import sys
import fosslight_util.constant as constant
import argparse
from yaml import safe_dump
from fosslight_util.set_log import init_log
from fosslight_util.spdx_licenses import get_spdx_licenses_json, get_license_from_nick
from fosslight_util.output_format import check_output_format
from fosslight_util.exclude import excluding_files
from datetime import datetime
from fosslight_prechecker._precheck import precheck_for_project, precheck_for_files, dump_error_msg, \
                                           get_path_to_find, DEFAULT_EXCLUDE_EXTENSION_FILES
from fosslight_prechecker._result import get_total_file_list
from fosslight_prechecker._add_header import add_header, reuse_parser
from reuse._comment import EXTENSION_COMMENT_STYLE_MAP_LOWERCASE
from reuse.project import Project
from typing import List, Optional


PKG_NAME = "fosslight_prechecker"
EXCLUDE_DIR = ["test", "tests", "doc", "docs"]
EXCLUDE_PREFIX = ("test", ".", "doc", "__")
_result_log = {}
spdx_licenses = []

logger = logging.getLogger(constant.LOGGER_NAME)


def convert_to_spdx_style(input_string: str) -> str:
    input_string = input_string.replace(" ", "-")
    input_converted = f"LicenseRef-{input_string}"
    return input_converted


def check_input_license_format(input_license: str) -> str:
    for spdx in spdx_licenses:
        if input_license.casefold() == spdx.casefold():
            return spdx

    if input_license.startswith('LicenseRef-'):
        return input_license

    licensesfromJson = get_license_from_nick()
    if licensesfromJson == "":
        dump_error_msg(" Error - Return Value to get license from Json is none")

    try:
        # Get frequetly used license from json file
        converted_license = licensesfromJson.get(input_license.casefold())
        if converted_license is None:
            converted_license = convert_to_spdx_style(input_license)
    except Exception as ex:
        dump_error_msg(f"Error - Get frequetly used license : {ex}")

    return converted_license


def check_input_copyright_format(input_copyright: str) -> bool:
    regex = re.compile(r'Copyright(\s)+(\(c\)\s)?\s*\d{4}(-\d{4})*(\s)+(\S)+')
    check_ok = True

    if regex.match(input_copyright) is None:
        logger.warning("(-c option) You have to input with following format - '<year> <name>'")
        check_ok = False

    return check_ok


def input_license_while_running() -> str:
    input_license = ""

    logger.info("# Select a license to write in the license missing files ")
    select = input("\t1.MIT\n \t2.Apache-2.0\n \t3.LGE-Proprietary\n \t4.Manual Input\n \t5.Not select now\n- Choose one from the list: ")
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


def input_copyright_while_running() -> Optional[str]:
    input_copyright = ""
    input_copyright = input("# Input Copyright to write in the copyright missing files (ex, <year> <name>): ")
    if input_copyright == 'Quit' or input_copyright == 'quit' or input_copyright == 'Q':
        return

    return input_copyright


def input_dl_url_while_running() -> Optional[str]:
    input_dl_url = ""
    input_dl_url = input("# Input Download URL to write to missing files (ex, https://github.com/fosslight/fosslight-prechecker): ")
    if input_dl_url == 'Quit' or input_dl_url == 'quit' or input_dl_url == 'Q':
        return

    return input_dl_url


def add_dl_url_into_file(
    main_parser: argparse.ArgumentParser,
    project: Project,
    path_to_find: str,
    input_dl_url: str,
    file_list: List[str]
) -> None:
    logger.info("\n# Adding Download Location into your files")
    logger.warning(f"  * Your input DownloadLocation : {input_dl_url}")
    add_dl_url_list = [os.path.join(path_to_find, file) for file in file_list]
    parsed_args = main_parser.parse_args(['addheader', '--dlurl', input_dl_url] + add_dl_url_list)

    try:
        add_header(parsed_args, project)
    except Exception as ex:
        dump_error_msg(f"Error_to_add_url : {ex}")


def add_license_into_file(
    main_parser: argparse.ArgumentParser,
    project: Project,
    input_license: str,
    file_list: List[str]
) -> None:
    converted_license = check_input_license_format(input_license)
    logger.warning(f"  * Your input license : {converted_license}")
    parsed_args = main_parser.parse_args(['addheader', '--license', str(converted_license)] + file_list)
    try:
        add_header(parsed_args, project)
    except Exception as ex:
        dump_error_msg(f"Error_call_run_in_license : {ex}")


def add_copyright_into_file(
    main_parser: argparse.ArgumentParser,
    project: Project,
    input_copyright: str,
    file_list: List[str]
) -> None:
    input_copyright = f"Copyright {input_copyright}"

    input_ok = check_input_copyright_format(input_copyright)
    if input_ok is False:
        return

    logger.warning(f"  * Your input Copyright : {input_copyright}")
    parsed_args = main_parser.parse_args(['addheader', '--copyright',
                                          f'SPDX-FileCopyrightText: {input_copyright}',
                                          '--exclude-year'] + file_list)
    try:
        add_header(parsed_args, project)
    except Exception as ex:
        dump_error_msg(f"Error_call_run_in_copyright : {ex}")


def set_missing_license_copyright(
    missing_license_filtered: Optional[List[str]],
    missing_copyright_filtered: Optional[List[str]],
    project: Project,
    path_to_find: str,
    license: str,
    copyright: str,
    total_files_excluded: List[str],
    input_dl_url: str
) -> None:
    input_license = ""
    input_copyright = ""

    try:
        main_parser = reuse_parser()
    except Exception as ex:
        dump_error_msg(f"Error_get_arg_parser : {ex}")

    if license == "" and copyright == "" and input_dl_url == "":
        input_license = input_license_while_running()
        input_copyright = input_copyright_while_running()
        input_dl_url = input_dl_url_while_running()
    else:
        input_license = license
        input_copyright = copyright

    # Add input_license into missing License files
    if missing_license_filtered is not None and len(missing_license_filtered) > 0:
        missing_license_list = []

        logger.info("# Missing license File(s)")
        for lic_file in sorted(missing_license_filtered):
            logger.info(f"  * {lic_file}")
            missing_license_list.append(os.path.join(path_to_find, lic_file))

        if input_license != "":
            add_license_into_file(main_parser, project, input_license, missing_license_list)
    else:
        logger.info("# There is no missing license file\n")

    # Add input_copyright into missing Copyright files
    if missing_copyright_filtered is not None and len(missing_copyright_filtered) > 0:
        missing_copyright_list = []

        logger.info("\n# Missing Copyright File(s) ")
        for cop_file in sorted(missing_copyright_filtered):
            logger.info(f"  * {cop_file}")
            missing_copyright_list.append(os.path.join(path_to_find, cop_file))

        if input_copyright != "":
            add_copyright_into_file(main_parser, project, input_copyright, missing_copyright_list)
    else:
        logger.info("\n# There is no missing copyright file\n")

    # Add input_dl_url into all files in input path
    if input_dl_url:
        add_dl_url_into_file(main_parser, project, path_to_find, input_dl_url, total_files_excluded)


def get_allfiles_list(path):
    try:
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                if dir.startswith(EXCLUDE_PREFIX):
                    dirs.remove(dir)
                    continue
            for file in files:
                file_abs_path = os.path.join(root, file)
                file_rel_path = os.path.relpath(file_abs_path, path)
                yield file_rel_path
    except Exception as ex:
        dump_error_msg(f"Error - get all files list : {ex}")


def save_result_log() -> None:
    try:
        _str_final_result_log = safe_dump(_result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning(f"Failed to print add result log. : {ex}")


def is_exclude_dir(dir_path: str) -> Optional[bool]:
    if dir_path != "":
        dir_path = dir_path.lower()
        dir_path = dir_path if dir_path.endswith(
            os.path.sep) else dir_path + os.path.sep
        dir_path = dir_path if dir_path.startswith(
            os.path.sep) else os.path.sep + dir_path
        return any(dir_name in dir_path for dir_name in EXCLUDE_DIR)
    return


def get_spdx_license_list():
    global spdx_licenses
    try:
        success, error_msg, licenses = get_spdx_licenses_json()
        if success is False:
            dump_error_msg(f"Error to get SPDX Licesens : {error_msg}")

        licenseInfo = licenses.get("licenses")
        for info in licenseInfo:
            shortID = info.get("licenseId")
            isDeprecated = info.get("isDeprecatedLicenseId")
            if isDeprecated is False:
                spdx_licenses.append(shortID)
    except Exception as ex:
        dump_error_msg(f"Error access to get_spdx_licenses_json : {ex}")


def add_content(
    target_path: str = "",
    input_license: str = "",
    input_copyright: str = "",
    input_dl_url: str = "",
    output_path: str = "",
    need_log_file: bool = True,
    exclude_path: list = []
) -> None:
    global _result_log
    _check_only_file_mode = False
    file_to_check_list = []
    missing_license = []

    path_to_find, file_to_check_list, _check_only_file_mode = get_path_to_find(target_path, _check_only_file_mode)

    _, _, output_path, _, _ = check_output_format(output_path)
    if output_path == "":
        output_path = os.getcwd()
    else:
        output_path = os.path.abspath(output_path)

    user_exclude_path = excluding_files(exclude_path, path_to_find)
    abs_path_to_exclude = [os.path.abspath(path) for path in user_exclude_path]

    now = datetime.now().strftime('%y%m%d_%H%M')
    logger, _result_log = init_log(os.path.join(output_path, f"fosslight_log_pre_{now}.txt"),
                                   need_log_file, logging.INFO, logging.DEBUG, PKG_NAME, path_to_find)

    if not os.path.isdir(path_to_find):
        logger.error(f"(-p option) Check the path to find : {path_to_find}")
        sys.exit(1)

    # Get SPDX License List
    get_spdx_license_list()

    if _check_only_file_mode:
        main_parser = reuse_parser()
        missing_license_list, missing_copyright_list, project = precheck_for_files(path_to_find, file_to_check_list)

        if input_license == "" and input_copyright == "" and input_dl_url == "":
            input_copyright = input_copyright_while_running()
            input_license = input_license_while_running()
            input_dl_url = input_dl_url_while_running()

        # Add License
        if missing_license_list is not None and len(missing_license_list) > 0:
            if input_license != "":
                add_license_into_file(main_parser, project, input_license, missing_license_list)

        else:
            logger.info("# There is no missing license file")

        # Add Copyright
        if missing_copyright_list is not None and len(missing_copyright_list) > 0:
            if input_copyright != "":
                add_copyright_into_file(main_parser, project, input_copyright, missing_copyright_list)
        else:
            logger.info("# There is no missing copyright file\n")

        # Add Download URL
        if input_dl_url:
            add_dl_url_into_file(main_parser, project, path_to_find, input_dl_url, file_to_check_list)
    else:
        # Get missing license / copyright file list
        missing_license, missing_copyright, _, project, prj_report = precheck_for_project(path_to_find, abs_path_to_exclude)

        # Get total files except excluded file
        total_files_excluded = get_total_file_list(path_to_find, prj_report, DEFAULT_EXCLUDE_EXTENSION_FILES, abs_path_to_exclude)
        skip_files = sorted(set(total_files_excluded) - set(missing_license) - set(missing_copyright))
        logger.info(f"\n# File list that have both license and copyright : {len(skip_files)} / {len(total_files_excluded)}")

        # Filter by file extension
        total_files_excluded = [file for file in total_files_excluded
                                if os.path.splitext(file)[1].lower() in EXTENSION_COMMENT_STYLE_MAP_LOWERCASE]
        missing_license = [file for file in missing_license if os.path.splitext(file)[1].lower() in EXTENSION_COMMENT_STYLE_MAP_LOWERCASE]
        missing_copyright = [file for file in missing_copyright if os.path.splitext(file)[1].lower() in EXTENSION_COMMENT_STYLE_MAP_LOWERCASE]

        # Check license and copyright of each file
        precheck_for_files(path_to_find, skip_files)

        # Set missing license and copyright
        set_missing_license_copyright(missing_license,
                                      missing_copyright,
                                      project,
                                      path_to_find,
                                      input_license,
                                      input_copyright,
                                      total_files_excluded,
                                      input_dl_url)
    save_result_log()

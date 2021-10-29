#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import re
import logging
import shutil
import json
import sys
import fosslight_util.constant as constant
from yaml import safe_dump
from fosslight_util.set_log import init_log
from fosslight_util.spdx_licenses import get_spdx_licenses_json
from datetime import datetime
from ._fosslight_reuse import reuse_for_project, reuse_for_files, print_error
from reuse.header import run as reuse_header
from reuse.download import run as reuse_download
from reuse._comment import EXTENSION_COMMENT_STYLE_MAP_LOWERCASE
from reuse._main import parser as reuse_arg_parser
from reuse.project import Project
from fosslight_oss_pkg._parsing_yaml import find_all_oss_pkg_files, parsing_yml


PKG_NAME = "fosslight_reuse"
LICENSE_INCLUDE_FILES = ["license", "license.md", "license.txt", "notice"]
EXCLUDE_DIR = ["test", "tests", "doc", "docs"]
EXCLUDE_PREFIX = ("test", ".", "doc", "__")
RESOURCES_DIR = 'resources'
LICENSES_JSON_FILE = 'convert_license.json'
_result_log = {}
spdx_licenses = []

logger = logging.getLogger(constant.LOGGER_NAME)


def get_licenses_from_json():
    licenses = {}
    licenses_file = os.path.join(RESOURCES_DIR, LICENSES_JSON_FILE)

    try:
        base_dir = sys._MEIPASS
    except Exception:
        base_dir = os.path.dirname(__file__)

    file_withpath = os.path.join(base_dir, licenses_file)
    try:
        with open(file_withpath, 'r') as f:
            licenses = json.load(f)
    except Exception as ex:
        print_error('Error to get license from json file :' + str(ex))

    return licenses


def check_file_extension(file_list):
    files_filtered = []

    if file_list != "":
        for file in file_list:
            try:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension == "":
                    logger.info(" No extension file(s) : " + file)
                if file_extension in EXTENSION_COMMENT_STYLE_MAP_LOWERCASE:
                    files_filtered.append(file)
            except Exception as ex:
                print_error("Error - Unknown error to check file extension - " + str(ex))

    return files_filtered


def check_license_and_copyright(path_to_find, all_files, missing_license, missing_copyright):
    # Check file extension for each list
    all_files_fitered = check_file_extension(all_files)
    missing_license_filtered = check_file_extension(missing_license)
    missing_copyright_filtered = check_file_extension(missing_copyright)

    skip_files = sorted(list(set(all_files_fitered) - set(missing_license_filtered) - set(missing_copyright_filtered)))
    logger.info(f"\n# File list that have both license and copyright : {len(skip_files)} / {len(all_files)}")

    file_list = list()
    for file in skip_files:
        file_list.append(file)

    reuse_for_files(path_to_find, file_list)

    return missing_license_filtered, missing_copyright_filtered


def convert_to_spdx_style(input_string):
    input_string = input_string.replace(" ", "-")
    input_converted = "LicenseRef-" + input_string
    return input_converted


def check_input_license_format(input_license):
    if input_license in spdx_licenses:
        return input_license

    if input_license.startswith('LicenseRef-'):
        return input_license

    licensesfromJson = get_licenses_from_json()
    if licensesfromJson == "":
        print_error(" Error - Return Value to get license from Json is none ")

    try:
        # Get frequetly used license from json file
        converted_license = licensesfromJson.get(input_license.lower())
        if converted_license is None:
            converted_license = convert_to_spdx_style(input_license)
    except Exception as ex:
        print_error(f"Error - Get frequetly used license : {ex}")

    return converted_license


def check_input_copyright_format(input_copyright):
    regex = re.compile(r'Copyright(\s)+(\(c\)\s)?\s*\d{4}(-\d{4})*(\s)+(\S)+')
    check_ok = True

    if regex.match(input_copyright) is None:
        logger.warning(" You have to input with following format - '<year> <name>'")
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
    input_copyright = input("# Input Copyright to write in the copyright missing files (ex, <year> <name>) : ")
    if input_copyright == 'Quit' or input_copyright == 'quit' or input_copyright == 'Q':
        return

    return input_copyright


def set_missing_license_copyright(missing_license_filtered, missing_copyright_filtered, project, path_to_find, license, copyright):
    input_license = ""
    input_copyright = ""

    try:
        main_parser = reuse_arg_parser()
    except Exception as ex:
        print_error('Error_get_arg_parser :' + str(ex))

    # Print missing License
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
            input_license = check_input_license_format(input_license)
            logger.warning(f"  * Your input license : {input_license}")
            parsed_args = main_parser.parse_args(['addheader', '--license', str(input_license)] + missing_license_list)
            try:
                reuse_header(parsed_args, project)
            except Exception as ex:
                print_error('Error_call_run_in_license :' + str(ex))
    else:
        logger.info("# There is no missing license file\n")

    # Print missing Copyright
    if missing_copyright_filtered is not None and len(missing_copyright_filtered) > 0:
        missing_copyright_list = []

        logger.info("\n# Missing Copyright File(s) ")
        for cop_file in sorted(missing_copyright_filtered):
            logger.info(f"  * {cop_file}")
            missing_copyright_list.append(cop_file)

        if license == "" and copyright == "":
            input_copyright = input_copyright_while_running()
        else:
            input_copyright = copyright

        if input_copyright != "":
            input_copyright = 'Copyright ' + input_copyright

            input_ok = check_input_copyright_format(input_copyright)
            if input_ok is False:
                return

            logger.warning(f"  * Your input Copyright : {input_copyright}")
            parsed_args = main_parser.parse_args(['addheader', '--copyright',
                                                  'SPDX-FileCopyrightText: ' + str(input_copyright),
                                                  '--exclude-year'] + missing_copyright_list)
            try:
                reuse_header(parsed_args, project)
            except Exception as ex:
                print_error('Error_call_run_in_copyright :' + str(ex))
    else:
        logger.info("\n# There is no missing copyright file\n")


def get_allfiles_list(path):
    all_files = []

    try:
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                if dir.startswith(EXCLUDE_PREFIX):
                    dirs.remove(dir)
                    continue
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


def copy_to_root(input_license):
    lic_file = str(input_license) + '.txt'
    try:
        source = os.path.join('LICENSES', f'{lic_file}')
        destination = 'LICENSE'
        shutil.copyfile(source, destination)
    except Exception as ex:
        print_error("Error - Can't copy license file: " + str(ex))


def find_representative_license(path_to_find, input_license):
    files = []
    found_file = []
    found_license_file = False
    main_parser = reuse_arg_parser()
    prj = Project(path_to_find)

    all_items = os.listdir(path_to_find)
    for item in all_items:
        if os.path.isfile(item):
            files.append(os.path.basename(item))

    for file in files:
        file_lower_case = file.lower()

        if file_lower_case in LICENSE_INCLUDE_FILES or file_lower_case.startswith("license") or file_lower_case.startswith("notice"):
            found_file.append(file)
            found_license_file = True

    if found_license_file:
        logger.warning(f" # Found representative license file : {found_file}")
    else:
        input_license = check_input_license_format(input_license)

        logger.info(f" Input License : {input_license}")
        parsed_args = main_parser.parse_args(['download', str(input_license)])

        try:
            logger.warning(" # There is no representative license file")
            reuse_download(parsed_args, prj)
            copy_to_root(input_license)
            if input_license in spdx_licenses:
                logger.warning(f" # Created Representative License File : {input_license}.txt")

        except Exception as ex:
            print_error('Error - download representative license text:' + str(ex))


def is_exclude_dir(dir_path):
    if dir_path != "":
        dir_path = dir_path.lower()
        dir_path = dir_path if dir_path.endswith(
            os.path.sep) else dir_path + os.path.sep
        dir_path = dir_path if dir_path.startswith(
            os.path.sep) else os.path.sep + dir_path
        return any(dir_name in dir_path for dir_name in EXCLUDE_DIR)
    return


def download_oss_info_license(base_path, input_license=""):
    oss_pkg_files = ["oss-pkg-info.yml", "oss-pkg-info.yaml"]
    license_list = []
    converted_lic_list = []
    main_parser = reuse_arg_parser()
    prj = Project(base_path)

    found_oss_pkg_files = find_all_oss_pkg_files(base_path, oss_pkg_files)

    if input_license != "":
        license_list.append(input_license)

    if found_oss_pkg_files is None or len(found_oss_pkg_files) == 0:
        logger.info("\n # There is no OSS package Info file in this path\n")
        return
    else:
        logger.info(f"\n # There is OSS Package Info file(s) : {found_oss_pkg_files}\n")

    for oss_pkg_file in found_oss_pkg_files:
        _, license_list = parsing_yml(oss_pkg_file, base_path)

    for lic in license_list:
        converted_lic_list.append(check_input_license_format(lic))

    if license_list is not None and len(license_list) > 0:
        parsed_args = main_parser.parse_args(['download'] + converted_lic_list)

        try:
            reuse_download(parsed_args, prj)
        except Exception as ex:
            print_error('Error - download license text in OSS-pkg-info.yml :' + str(ex))
    else:
        logger.info(" # There is no license in the path \n")


def add_content(path_to_find="", file="", input_license="", input_copyright=""):
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
                                   True, logging.INFO, logging.DEBUG, PKG_NAME, path_to_find)

    if file != "":
        file_to_check_list = file.split(',')
        _check_only_file_mode = True

    # Get SPDX License List
    try:
        success, error_msg, licenses = get_spdx_licenses_json()
        if success is False:
            print_error('Error to get SPDX Licesens : ' + str(error_msg))

        licenseInfo = licenses.get("licenses")
        for info in licenseInfo:
            shortID = info.get("licenseId")
            isDeprecated = info.get("isDeprecatedLicenseId")
            if isDeprecated is False:
                spdx_licenses.append(shortID)
    except Exception as ex:
        print_error('Error access to get_spdx_licenses_json : ' + str(ex))

    if input_license != "":
        find_representative_license(path_to_find, input_license)

    # Download license text file of OSS-pkg-info.yaml
    download_oss_info_license(path_to_find, input_license)

    # File Only mode (-f option)
    if _check_only_file_mode:
        main_parser = reuse_arg_parser()
        missing_license_list, missing_copyright_list, error_occurred, project = reuse_for_files(path_to_find, file_to_check_list)

        if missing_license_list is not None and len(missing_license_list) > 0:
            if input_license == "" and input_copyright == "":
                input_license = input_license_while_running()

            if input_license != "":
                converted_license = check_input_license_format(input_license)
                logger.warning(f"  * Your input license : {converted_license}")
                parsed_args = main_parser.parse_args(['addheader', '--license', str(converted_license)] + missing_license_list)
                try:
                    reuse_header(parsed_args, project)
                except Exception as ex:
                    print_error('Error_call_run_in_license_file_only :' + str(ex))
        else:
            logger.info("# There is no missing license file")

        if missing_copyright_list is not None and len(missing_copyright_list) > 0:
            if input_license == "" and input_copyright == "":
                input_copyright = input_copyright_while_running()

            if input_copyright != "":
                input_copyright = 'Copyright ' + input_copyright

                input_ok = check_input_copyright_format(input_copyright)
                if input_ok is False:
                    return

                logger.warning(f"  * Your input Copyright : {input_copyright}")
                parsed_args = main_parser.parse_args(['addheader', '--copyright',
                                                      'SPDX-FileCopyrightText: ' + str(input_copyright),
                                                      '--exclude-year'] + missing_copyright_list)
            try:
                reuse_header(parsed_args, project)
            except Exception as ex:
                print_error('Error_call_run_in_copyright_file_only :' + str(ex))
        else:
            logger.info("# There is no missing copyright file\n")
    # Path mode (-p option)
    else:
        # Get all files List in path
        all_files_list = get_allfiles_list(path_to_find)

        # Get missing license / copyright file list
        _, missing_license, missing_copyright, _, _, project = reuse_for_project(path_to_find)

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

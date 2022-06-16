#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import sys
import shutil
import logging
import locale
import re
from datetime import datetime
from binaryornot.check import is_binary
import fosslight_util.constant as constant
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
from fosslight_util.parsing_yaml import parsing_yml, find_all_oss_pkg_files
from reuse import report
from reuse.project import Project
from reuse.report import ProjectReport
from fosslight_reuse._result import write_result_file, create_result_file, result_for_summary, ResultItem
from fosslight_reuse._constant import DEFAULT_EXCLUDE_EXTENSION, OSS_PKG_INFO_FILES

PKG_NAME = "fosslight_reuse"
REUSE_CONFIG_FILE = ".reuse/dep5"
DEFAULT_EXCLUDE_EXTENSION_FILES = []  # Exclude files from reuse
_turn_on_default_reuse_config = True
_check_only_file_mode = False
error_items = []
_start_time = ""
_result_log = {}

logger = logging.getLogger(constant.LOGGER_NAME)


def find_oss_pkg_info(path):
    global DEFAULT_EXCLUDE_EXTENSION_FILES
    oss_pkg_info = []

    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_lower_case = file.lower()
                file_abs_path = os.path.join(root, file)
                file_rel_path = os.path.relpath(file_abs_path, path)

                if any(re.search(re_oss_pkg_pattern, file_lower_case) for re_oss_pkg_pattern in OSS_PKG_INFO_FILES) \
                   or file_lower_case.startswith("module_license_"):
                    oss_pkg_info.append(file_rel_path)
                elif is_binary(file_abs_path):
                    DEFAULT_EXCLUDE_EXTENSION_FILES.append(file_rel_path)
                else:
                    extension = file_lower_case.split(".")[-1]
                    if extension in DEFAULT_EXCLUDE_EXTENSION:
                        DEFAULT_EXCLUDE_EXTENSION_FILES.append(file_rel_path)

    except Exception as ex:
        dump_error_msg(f"Error_FIND_OSS_PKG : {ex}")

    return oss_pkg_info


def create_reuse_dep5_file(path):
    # Create .reuse/dep5 for excluding directories from reuse.
    _DEFAULT_CONFIG_PREFIX = "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\nUpstream-Name: \
                        reuse\nUpstream-Contact: Carmen Bianca Bakker <carmenbianca@fsfe.org>\nSource: https://github.com/fsfe/reuse-tool\n"
    _DEFAULT_EXCLUDE_FOLDERS = ["venv*/*", "node_modules*/*", ".*/*"]

    reuse_config_file = os.path.join(path, REUSE_CONFIG_FILE)
    file_to_remove = reuse_config_file
    dir_to_remove = os.path.dirname(reuse_config_file)
    need_rollback = False
    str_contents = ""

    try:
        if not os.path.exists(dir_to_remove):
            os.makedirs(dir_to_remove, exist_ok=True)
        else:
            dir_to_remove = ""
        if os.path.exists(reuse_config_file):
            file_to_remove = f"{reuse_config_file}_{_start_time}.bk"
            shutil.copy2(reuse_config_file, file_to_remove)
            need_rollback = True

        DEFAULT_EXCLUDE_EXTENSION_FILES.extend(_DEFAULT_EXCLUDE_FOLDERS)
        for file_to_exclude in DEFAULT_EXCLUDE_EXTENSION_FILES:
            str_contents += f"\nFiles: {file_to_exclude} \nCopyright: -\nLicense: -\n"

        with open(reuse_config_file, "a") as f:
            if not need_rollback:
                f.write(_DEFAULT_CONFIG_PREFIX)
            f.write(str_contents)
    except Exception as ex:
        dump_error_msg(f"Error_Create_Dep5 : {ex}")

    return need_rollback, file_to_remove, dir_to_remove


def remove_reuse_dep5_file(rollback, file_to_remove, temp_dir_name):
    try:
        if rollback:
            _origin_file = os.path.join(os.path.dirname(file_to_remove), os.path.basename(REUSE_CONFIG_FILE))
            shutil.copy2(file_to_remove, _origin_file)

        os.remove(file_to_remove)

        if temp_dir_name != "":
            os.rmdir(temp_dir_name)

    except Exception as ex:
        dump_error_msg(f"Error_Remove_Dep5 : {ex}")


def reuse_for_files(path, files):
    global DEFAULT_EXCLUDE_EXTENSION_FILES

    missing_license_list = []
    missing_copyright_list = []

    try:
        prj = Project(path)

        for file in files:
            try:
                file_abs_path = os.path.join(path, file)
                if not os.path.isfile(file_abs_path) or is_binary(file_abs_path):
                    DEFAULT_EXCLUDE_EXTENSION_FILES.append(file)
                else:
                    extension = file.split(".")[-1]
                    if extension in DEFAULT_EXCLUDE_EXTENSION:
                        DEFAULT_EXCLUDE_EXTENSION_FILES.append(file)
                    else:
                        logger.info(f"# {file}")
                        rep = report.FileReport.generate(prj, file_abs_path)

                        logger.info(f"* License: {', '.join(rep.spdxfile.licenses_in_file)}")
                        logger.info(f"* Copyright: {rep.spdxfile.copyright}\n")

                        if rep.spdxfile.licenses_in_file is None or len(rep.spdxfile.licenses_in_file) == 0:
                            missing_license_list.append(file)
                        if rep.spdxfile.copyright is None or len(rep.spdxfile.copyright) == 0:
                            missing_copyright_list.append(file)

            except Exception as ex:
                dump_error_msg(f"Error_Reuse_for_file_to_read : {ex}", True)

    except Exception as ex:
        dump_error_msg(f"Error_Reuse_for_file : {ex}", True)

    return missing_license_list, missing_copyright_list, prj


def extract_files_in_path(repository, filepath):
    extract_files = []
    for path in filepath:
        if not repository.endswith("/"):
            repository += "/"
        if os.path.isdir(path):
            files = os.listdir(path)
            files = [os.path.join(path, file) for file in files]
            files = [sub.replace(repository, '') for sub in files]
            extract_files.extend(files)
        elif os.path.isfile(path):
            path = path.replace(repository, '')
            extract_files.append(path)
    return extract_files


def get_rel_path_in_yaml(oss_item):
    for source_name_or_path in oss_item.source_name_or_path:
        yield os.path.join(oss_item.relative_path, source_name_or_path)


# TODO : Get all file list in 'exclude_filepath' by using Regular expression
def get_excluded_file_in_yaml(repository, yaml_files):
    excluded_path = []
    excluded_list = []
    lic_present_path = []
    lic_present_list = []
    cop_present_path = []
    cop_present_list = []

    for file in yaml_files:
        oss_items, _ = parsing_yml(file, repository)
        for oss_item in oss_items:
            if oss_item.exclude:
                excluded_path = get_rel_path_in_yaml(oss_item)
                excluded_list.extend(extract_files_in_path(repository, excluded_path))
            if oss_item.license:
                lic_present_path = get_rel_path_in_yaml(oss_item)
                lic_present_list.extend(extract_files_in_path(repository, lic_present_path))
            if oss_item.copyright:
                cop_present_path = get_rel_path_in_yaml(oss_item)
                cop_present_list.extend(extract_files_in_path(repository, cop_present_path))
    return excluded_list, lic_present_list, cop_present_list


def get_only_pkg_info_yaml_file(pkg_info_files):
    for yaml in pkg_info_files:
        if yaml.split('/')[-1].startswith("oss-pkg-info"):
            yield yaml


def reuse_for_project(path_to_find):
    missing_license = []
    missing_copyright = []
    pkg_info_yaml_files = []
    excluded_files = []
    lic_present_files_in_yaml = []
    cop_present_files_in_yaml = []
    yaml_file = []

    oss_pkg_info_files = find_oss_pkg_info(path_to_find)
    if _turn_on_default_reuse_config:
        need_rollback, temp_file_name, temp_dir_name = create_reuse_dep5_file(path_to_find)

    try:
        # Use ProgressBar
        timer = TimerThread()
        timer.setDaemon(True)
        timer.start()

        project = Project(path_to_find)
        report = ProjectReport.generate(project)

        timer.stop = True

        if oss_pkg_info_files:
            pkg_info_yaml_files = find_all_oss_pkg_files(path_to_find, oss_pkg_info_files)
            yaml_file = get_only_pkg_info_yaml_file(pkg_info_yaml_files)

            # Get path to be excluded in yaml file
            excluded_files, lic_present_files_in_yaml, cop_present_files_in_yaml = get_excluded_file_in_yaml(path_to_find, yaml_file)

        # File list that missing license text
        missing_license = [str(sub) for sub in set(report.files_without_licenses)]
        if not path_to_find.endswith("/"):
            path_to_find += "/"
        missing_license = [sub.replace(path_to_find, '') for sub in missing_license]

        # File list that missing copyright text
        missing_copyright = [str(sub) for sub in set(report.files_without_copyright)]
        if not path_to_find.endswith("/"):
            path_to_find += "/"
        missing_copyright = [sub.replace(path_to_find, '') for sub in missing_copyright]
    except Exception as ex:
        dump_error_msg(f"Error_Reuse_lint: {ex}", True)

    if _turn_on_default_reuse_config:
        remove_reuse_dep5_file(need_rollback, temp_file_name, temp_dir_name)
    return missing_license, missing_copyright, oss_pkg_info_files, project, \
        report, excluded_files, lic_present_files_in_yaml, cop_present_files_in_yaml


def dump_error_msg(error_msg: str, exit=False):
    global error_items
    error_items.append(error_msg)
    if exit:
        logger.error(error_msg)
        sys.exit(1)


def init(path_to_find, output_path, file_list, need_log_file=True):
    global logger, _result_log
    logger, _result_log = init_log(os.path.join(output_path, f"fosslight_reuse_log_{_start_time}.txt"),
                                   need_log_file, logging.INFO, logging.DEBUG, PKG_NAME, path_to_find)
    if file_list:
        _result_log["File list to check"] = file_list


def get_path_to_find(target_path, _check_only_file_mode):
    is_file = False
    is_folder = False
    file_to_check_list = []
    path_list = []
    path_to_find = ""

    path_list = target_path.split(',')
    # Check if all elements are only files or folder
    for path in path_list:
        if os.path.isdir(path) and not is_folder:
            is_folder = True
            if path == "":
                path_to_find = os.getcwd()
            else:
                path_to_find = os.path.relpath(path)
        elif os.path.isfile(path):
            is_file = True
            path_to_find = os.getcwd()

    if is_file and is_folder:
        logger.error("Input only a folder or files with -p option")
    elif not is_folder and is_file:
        file_to_check_list = path_list
        _check_only_file_mode = True

    return path_to_find, file_to_check_list, _check_only_file_mode


def run_lint(target_path, disable, output_file_name, format='', need_log_file=True):
    global _turn_on_default_reuse_config, _check_only_file_mode, _start_time

    file_to_check_list = []
    _exit_code = os.EX_OK
    path_to_find = ""
    report = ProjectReport()
    result_item = ResultItem()
    success = False
    _start_time = datetime.now().strftime('%Y%m%d_%H-%M-%S')

    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except Exception as ex:
        dump_error_msg(f"Error - locale : {ex}")

    path_to_find, file_to_check_list, _check_only_file_mode = get_path_to_find(target_path, _check_only_file_mode)

    result_file, output_path, output_extension = create_result_file(output_file_name, format, _start_time)
    init(path_to_find, output_path, file_to_check_list, need_log_file)

    if os.path.isdir(path_to_find):
        lic_present_files_in_yaml = []
        cop_present_files_in_yaml = []
        excluded_files = []
        oss_pkg_info = []
        _turn_on_default_reuse_config = not disable

        if _check_only_file_mode:
            license_missing_files, copyright_missing_files, project = reuse_for_files(path_to_find, file_to_check_list)
        else:
            license_missing_files, copyright_missing_files, oss_pkg_info, project, \
                report, excluded_files, lic_present_files_in_yaml, cop_present_files_in_yaml = reuse_for_project(path_to_find)

        result_item = result_for_summary(oss_pkg_info,
                                         license_missing_files,
                                         copyright_missing_files,
                                         report,
                                         _result_log,
                                         _check_only_file_mode,
                                         file_to_check_list,
                                         error_items,
                                         excluded_files,
                                         lic_present_files_in_yaml,
                                         cop_present_files_in_yaml)

        success, exit_code = write_result_file(result_file, output_extension, _exit_code, result_item, _result_log)
        if success:
            logger.warning(f"Created file name: {result_file}\n")
        else:
            logger.warning("Can't make result file\n")
        sys.exit(exit_code)
    else:
        logger.error(f"Check the path to find : {path_to_find}")
        sys.exit(1)

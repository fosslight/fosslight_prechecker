#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import sys
import shutil
import logging
import locale
import platform
import re
import subprocess
from datetime import datetime
from binaryornot.check import is_binary
import fosslight_util.constant as constant
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
from reuse import report
from reuse.project import Project
from reuse.report import ProjectReport
from reuse.vcs import VCSStrategyGit
from fosslight_prechecker._result import write_result_file, create_result_file, result_for_summary, ResultItem
from fosslight_prechecker._constant import DEFAULT_EXCLUDE_EXTENSION, OSS_PKG_INFO_FILES, PKG_NAME

is_windows = platform.system() == 'Windows'
REUSE_CONFIG_FILE = ".reuse/dep5"
DEFAULT_EXCLUDE_EXTENSION_FILES = []  # Exclude files from reuse
_turn_on_exclude_config = True
_check_only_file_mode = False
error_items = []
_start_time = ""
_result_log = {}

logger = logging.getLogger(constant.LOGGER_NAME)


def exclude_untracked_files(path):
    global DEFAULT_EXCLUDE_EXTENSION_FILES
    try:
        cmd_result = subprocess.check_output(['git', 'ls-files', '-o'], universal_newlines=True)
        cmd_result = cmd_result.split('\n')
        cmd_result.remove('')
        if not path.endswith(f"{os.sep}"):
            path += f"{os.sep}"
        cmd_result = [file.replace(path, '', 1) for file in cmd_result]
        DEFAULT_EXCLUDE_EXTENSION_FILES.extend(cmd_result)
    except Exception as ex:
        logger.error(f"Error to get git untracked files : {ex}")


def exclude_gitignore_files(current_path, path):
    global DEFAULT_EXCLUDE_EXTENSION_FILES
    try:
        root_path = VCSStrategyGit.find_root(current_path)
        if os.path.isfile(os.path.join(root_path, '.gitignore')):
            cmd_result = subprocess.check_output(['git',
                                                  'ls-files',
                                                  '-i',
                                                  '--exclude-from=.gitignore'],
                                                 universal_newlines=True)
            cmd_result = cmd_result.split('\n')
            cmd_result.remove('')
            if not path.endswith(f"{os.sep}"):
                path += f"{os.sep}"
            cmd_result = [file.replace(path, '', 1) for file in cmd_result]
            DEFAULT_EXCLUDE_EXTENSION_FILES.extend(cmd_result)
        else:
            return

    except Exception as ex:
        logger.error(f"Error to get git ignored files : {ex}")


def exclude_git_related_files(path):
    try:
        # Change currnt path for git command
        current_path = os.getcwd()
        os.chdir(path)

        # Exclude untracked files
        exclude_untracked_files(path)
        # Exclude ignore files
        exclude_gitignore_files(current_path, path)

        # Restore path
        os.chdir(current_path)
    except Exception as ex:
        logger.error(f"Error to get git related files : {ex}")


def find_oss_pkg_info_and_exlcude_file(path, mode='lint'):
    global DEFAULT_EXCLUDE_EXTENSION_FILES
    oss_pkg_info = []
    git_present = shutil.which("git")

    if mode == 'lint' and _turn_on_exclude_config and git_present and VCSStrategyGit.in_repo(path):
        exclude_git_related_files(path)

    try:
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                # For hidden folders
                if dir.startswith("."):
                    all_files_in_dir = [os.path.join(root, dir, file)
                                        for file in os.listdir(os.path.join(root, dir))
                                        if os.path.isfile(os.path.join(root, dir, file))]
                    all_files_rel_path = [os.path.relpath(file, path) for file in all_files_in_dir]
                    DEFAULT_EXCLUDE_EXTENSION_FILES.extend(all_files_rel_path)

            for file in files:
                file_lower_case = file.lower()
                file_abs_path = os.path.join(root, file)
                file_rel_path = os.path.relpath(file_abs_path, path)

                if any(re.search(re_oss_pkg_pattern, file_lower_case) for re_oss_pkg_pattern in OSS_PKG_INFO_FILES) \
                   or file_lower_case.startswith("module_license_"):
                    oss_pkg_info.append(file_rel_path)
                # Exclude hidden files
                elif _turn_on_exclude_config and file.startswith('.'):
                    DEFAULT_EXCLUDE_EXTENSION_FILES.append(file_rel_path)
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
    global DEFAULT_EXCLUDE_EXTENSION_FILES
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
        exclude_file_list = list(set(DEFAULT_EXCLUDE_EXTENSION_FILES))

        if is_windows:
            exclude_file_list = [file.replace(os.sep, '/') for file in exclude_file_list]

        for file_to_exclude in exclude_file_list:
            str_contents += f"\nFiles: {file_to_exclude} \nCopyright: -\nLicense: -\n"

        with open(reuse_config_file, "a", encoding="utf8") as f:
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


def precheck_for_files(path, files):
    global DEFAULT_EXCLUDE_EXTENSION_FILES

    missing_license_list = []
    missing_copyright_list = []

    try:
        prj = Project(path)

        for file in files:
            try:
                file_abs_path = os.path.join(path, file)
                if not os.path.isfile(file_abs_path) or is_binary(file_abs_path):
                    if is_windows:
                        file = file.replace(os.sep, '/')
                    DEFAULT_EXCLUDE_EXTENSION_FILES.append(file)
                else:
                    extension = file.split(".")[-1]
                    if extension in DEFAULT_EXCLUDE_EXTENSION:
                        if is_windows:
                            file = file.replace(os.sep, '/')
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
                dump_error_msg(f"Error - precheck_for_files to read : {ex}", True)

    except Exception as ex:
        dump_error_msg(f"Error - precheck_for_files: {ex}", True)

    return missing_license_list, missing_copyright_list, prj


def precheck_for_project(path_to_find, mode='lint'):
    missing_license = []
    missing_copyright = []

    oss_pkg_info_files = find_oss_pkg_info_and_exlcude_file(path_to_find, mode)
    if _turn_on_exclude_config:
        need_rollback, temp_file_name, temp_dir_name = create_reuse_dep5_file(path_to_find)

    try:
        project = Project(path_to_find)
        report = ProjectReport.generate(project)

        # File list that missing license text
        missing_license = [str(sub) for sub in set(report.files_without_licenses)]
        if not path_to_find.endswith(f"{os.sep}"):
            path_to_find += f"{os.sep}"
        missing_license = [sub.replace(path_to_find, '') for sub in missing_license]

        # File list that missing copyright text
        missing_copyright = [str(sub) for sub in set(report.files_without_copyright)]
        if not path_to_find.endswith(f"{os.sep}"):
            path_to_find += f"{os.sep}"
        missing_copyright = [sub.replace(path_to_find, '') for sub in missing_copyright]
    except Exception as ex:
        dump_error_msg(f"Error prechecker lint: {ex}", True)

    if _turn_on_exclude_config:
        remove_reuse_dep5_file(need_rollback, temp_file_name, temp_dir_name)
    return missing_license, missing_copyright, oss_pkg_info_files, project, report


def dump_error_msg(error_msg: str, exit=False):
    global error_items
    error_items.append(error_msg)
    if exit:
        logger.error(error_msg)
        sys.exit(1)


def init(path_to_find, output_path, file_list, need_log_file=True):
    global logger, _result_log
    logger, _result_log = init_log(os.path.join(output_path, f"fosslight_log_{_start_time}.txt"),
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
    global _turn_on_exclude_config, _check_only_file_mode, _start_time

    file_to_check_list = []
    _exit_code = 0
    path_to_find = ""
    report = ProjectReport()
    result_item = ResultItem()
    success = False
    _start_time = datetime.now().strftime('%y%m%d_%H%M')

    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except Exception as ex:
        dump_error_msg(f"Error - locale : {ex}")

    path_to_find, file_to_check_list, _check_only_file_mode = get_path_to_find(target_path, _check_only_file_mode)

    result_file, output_path, output_extension = create_result_file(output_file_name, format, _start_time)
    init(path_to_find, output_path, file_to_check_list, need_log_file)

    if os.path.isdir(path_to_find):
        oss_pkg_info = []
        _turn_on_exclude_config = not disable

        if need_log_file:
            # Use ProgressBar
            timer = TimerThread()
            timer.setDaemon(True)
            timer.start()

        if _check_only_file_mode:
            license_missing_files, copyright_missing_files, project = precheck_for_files(path_to_find, file_to_check_list)
        else:
            license_missing_files, copyright_missing_files, oss_pkg_info, project, report = precheck_for_project(path_to_find, 'lint')

        if need_log_file:
            timer.stop = True

        result_item = result_for_summary(path_to_find,
                                         oss_pkg_info,
                                         license_missing_files,
                                         copyright_missing_files,
                                         report,
                                         _result_log,
                                         _check_only_file_mode,
                                         file_to_check_list,
                                         error_items,
                                         DEFAULT_EXCLUDE_EXTENSION_FILES)

        success, exit_code = write_result_file(result_file, output_extension, _exit_code,
                                               result_item, _result_log, project, path_to_find)
        if success:
            logger.warning(f"Created file name: {result_file}\n")
        else:
            logger.warning("Can't make result file\n")
        sys.exit(exit_code)
    else:
        logger.error(f"Check the path to find : {target_path}")
        sys.exit(1)

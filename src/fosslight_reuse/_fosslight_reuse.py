#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import logging
import locale
from datetime import datetime
from binaryornot.check import is_binary
from pathlib import Path
import fosslight_util.constant as constant
from fosslight_util.set_log import init_log
from fosslight_util.timer_thread import TimerThread
from fosslight_util.parsing_yaml import parsing_yml, find_all_oss_pkg_files
from fosslight_util.output_format import check_output_format
from yaml import safe_dump
from reuse import report
from reuse.project import Project
from reuse.report import ProjectReport


_PKG_NAME = "fosslight_reuse"
_RULE_LINK = "https://oss.lge.com/guide/process/osc_process/1-identification/copyright_license_rule.html"
_MSG_REFERENCE = "Ref. Copyright and License Writing Rules in Source Code. : " + _RULE_LINK
_MSG_FOLLOW_LIC_TXT = "Follow the Copyright and License Writing Rules in Source Code. : " + _RULE_LINK
_REUSE_CONFIG_FILE = ".reuse/dep5"
_DEFAULT_EXCLUDE_EXTENSION_FILES = []  # Exclude files from reuse
_DEFAULT_EXCLUDE_EXTENSION = ["jar", "png", "exe", "so", "a", "dll", "jpeg", "jpg", "ttf", "lib", "ttc", "pfb",
                              "pfm", "otf", "afm", "dfont", "json"]
_CUSTOMIZED_FORMAT_FOR_REUSE = {'html': '.html', 'xml': '.xml', 'yaml': '.yaml'}
_turn_on_default_reuse_config = True
_check_only_file_mode = False
_root_xml_item = ET.Element('results')
_start_time = ""
_result_log = {}

logger = logging.getLogger(constant.LOGGER_NAME)


def find_oss_pkg_info(path):
    global _DEFAULT_EXCLUDE_EXTENSION_FILES
    _OSS_PKG_INFO_FILES = ["oss-pkg-info.yaml", "oss-pkg-info.yml", "oss-package.info", "requirement.txt",
                           "requirements.txt", "package.json", "pom.xml",
                           "build.gradle",
                           "podfile.lock", "cartfile.resolved"]
    oss_pkg_info = []

    try:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_lower_case = file.lower()
                file_abs_path = os.path.join(root, file)
                file_rel_path = os.path.relpath(file_abs_path, path)

                if file_lower_case in _OSS_PKG_INFO_FILES or file_lower_case.startswith("module_license_"):
                    oss_pkg_info.append(file_rel_path)
                elif is_binary(file_abs_path):
                    _DEFAULT_EXCLUDE_EXTENSION_FILES.append(file_rel_path)
                else:
                    extension = file_lower_case.split(".")[-1]
                    if extension in _DEFAULT_EXCLUDE_EXTENSION:
                        _DEFAULT_EXCLUDE_EXTENSION_FILES.append(file_rel_path)

    except Exception as ex:
        print_error(f"Error_FIND_OSS_PKG : {ex}")

    return oss_pkg_info


def create_reuse_dep5_file(path):
    # Create .reuse/dep5 for excluding directories from reuse.
    _DEFAULT_CONFIG_PREFIX = "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\nUpstream-Name: \
                        reuse\nUpstream-Contact: Carmen Bianca Bakker <carmenbianca@fsfe.org>\nSource: https://github.com/fsfe/reuse-tool\n"
    _DEFAULT_EXCLUDE_FOLDERS = ["venv*/*", "node_modules*/*", ".*/*"]

    reuse_config_file = os.path.join(path, _REUSE_CONFIG_FILE)
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

        _DEFAULT_EXCLUDE_EXTENSION_FILES.extend(_DEFAULT_EXCLUDE_FOLDERS)
        for file_to_exclude in _DEFAULT_EXCLUDE_EXTENSION_FILES:
            str_contents += f"\nFiles: {file_to_exclude} \nCopyright: -\nLicense: -\n"

        with open(reuse_config_file, "a") as f:
            if not need_rollback:
                f.write(_DEFAULT_CONFIG_PREFIX)
            f.write(str_contents)
    except Exception as ex:
        print_error(f"Error_Create_Dep5 : {ex}")

    return need_rollback, file_to_remove, dir_to_remove


def remove_reuse_dep5_file(rollback, file_to_remove, temp_dir_name):
    try:
        if rollback:
            _origin_file = os.path.join(os.path.dirname(file_to_remove), os.path.basename(_REUSE_CONFIG_FILE))
            shutil.copy2(file_to_remove, _origin_file)

        os.remove(file_to_remove)

        if temp_dir_name != "":
            os.rmdir(temp_dir_name)

    except Exception as ex:
        print_error(f"Error_Remove_Dep5 : {ex}")


def reuse_for_files(path, files):
    global _DEFAULT_EXCLUDE_EXTENSION_FILES

    missing_license_list = []
    missing_copyright_list = []
    error_occurred = False

    try:
        prj = Project(path)

        for file in files:
            try:
                file_abs_path = os.path.join(path, file)
                if not os.path.isfile(file_abs_path) or is_binary(file_abs_path):
                    _DEFAULT_EXCLUDE_EXTENSION_FILES.append(file)
                else:
                    extension = file.split(".")[-1]
                    if extension in _DEFAULT_EXCLUDE_EXTENSION:
                        _DEFAULT_EXCLUDE_EXTENSION_FILES.append(file)
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
                print_error(f"Error_Reuse_for_file_to_read : {ex}")

    except Exception as ex:
        print_error(f"Error_Reuse_for_file : {ex}")
        error_occurred = True

    return missing_license_list, missing_copyright_list, error_occurred, prj


def extract_files_in_path(filepath):
    extract_files = []
    for path in filepath:
        if os.path.isdir(path):
            files = os.listdir(path)
            files = [os.path.join(path, file) for file in files]
            extract_files.extend(files)
        elif os.path.isfile(path):
            extract_files.append(path)
    return extract_files


def get_excluded_path_in_yaml(repository, yaml_files):
    for file in yaml_files:
        oss_list, _ = parsing_yml(file, repository)

        # if exclude filed is True, yield 'file' in pkg-info.yaml file
        for ossitem in oss_list:
            # If 'Exclude' field is true,
            if ossitem[9]:
                yield ossitem[1]


def get_only_pkg_info_yaml_file(pkg_info_files):
    for yaml in pkg_info_files:
        if yaml.split('/')[-1].startswith("oss-pkg-info"):
            yield yaml


def reuse_for_project(path_to_find):
    result = ""
    missing_license = []
    missing_copyright = []
    error_occured = False

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

        pkg_info_yaml_files = find_all_oss_pkg_files(path_to_find, oss_pkg_info_files)
        yaml_file = get_only_pkg_info_yaml_file(pkg_info_yaml_files)

        # Get path to be excluded in yaml file
        filepath_in_yaml = set(get_excluded_path_in_yaml(path_to_find, yaml_file))

        # TO DO
        # Get all file list in 'exclude_filepath' by using Regular expression
        excluded_files = extract_files_in_path(filepath_in_yaml)

        file_total = len(report.file_reports)
        timer.stop = True

        # Summary Message
        result += "* Used licenses:"
        for i, lic in enumerate(sorted(report.used_licenses)):
            if i:
                result += ","
            result += " "
            result += lic

        result += ("\n* Files with copyright information: {count} / {total}").format(
            count=file_total - len(report.files_without_copyright - set(excluded_files)),
            total=file_total
        )

        result += ("\n* Files with license information: {count} / {total}").format(
            count=file_total - len(report.files_without_licenses - set(excluded_files)),
            total=file_total
        )

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
        print_error(f"Error_Reuse_lint: {ex}")
        error_occured = True

    logger.warning(f"missing_license : {missing_license}")

    if _turn_on_default_reuse_config:
        remove_reuse_dep5_file(need_rollback, temp_file_name, temp_dir_name)
    return result, missing_license, missing_copyright, oss_pkg_info_files, error_occured, project


def print_error(error_msg: str):
    global _root_xml_item
    error_item = ET.Element('system_error')
    error_item.text = error_msg
    _root_xml_item.append(error_item)


def result_for_summary(str_lint_result, oss_pkg_info, path, msg_missing_files):
    global _root_xml_item

    reuse_compliant = False
    str_oss_pkg = "* Open Source Package info: "
    try:
        if oss_pkg_info is not None and len(oss_pkg_info) > 0:
            reuse_compliant = True
            str_oss_pkg += ", ".join(oss_pkg_info)
    except Exception as ex:
        print_error(f"Error_Print_OSS_PKG_INFO: {ex}")

    if msg_missing_files == "":
        reuse_compliant = True

    # Add Summary Comment
    _SUMMARY_PREFIX = '\n# SUMMARY\n'
    _SUMMARY_SUFFIX = '\n\n' + _MSG_REFERENCE
    str_summary = f"{_SUMMARY_PREFIX}{str_oss_pkg}\n{str_lint_result}{_SUMMARY_SUFFIX}"
    items = ET.Element('error')
    items.set('id', 'rule_key_osc_checker_01')
    items.set('line', '0')
    items.set('msg', str_summary)
    if not reuse_compliant:
        _root_xml_item.append(items)

    logger.info(msg_missing_files + str_summary)


def result_for_missing_license_and_copyright_files(files_without_license, files_without_copyright, oss_pkg_info):
    global _root_xml_item
    message = ""
    # If the oss_pkg_file exists,
    # it is unnecessary to print the result for each file without a license.
    if oss_pkg_info is not None and len(oss_pkg_info) > 0:
        print_mode = False
    else:
        print_mode = True

    str_missing_lic_files = ""
    str_missing_cop_files = ""
    for file_name in files_without_license:
        items = ET.Element('error')
        items.set('file', file_name)
        items.set('id', 'rule_key_osc_checker_02')
        items.set('line', '0')
        items.set('msg', _MSG_FOLLOW_LIC_TXT)
        if _check_only_file_mode:
            _root_xml_item.append(items)
        str_missing_lic_files += (f"* {file_name}\n")

    for file_name in files_without_copyright:
        items = ET.Element('error')
        items.set('file', file_name)
        items.set('id', 'rule_key_osc_checker_02')
        items.set('line', '0')
        items.set('msg', _MSG_FOLLOW_LIC_TXT)
        if _check_only_file_mode:
            _root_xml_item.append(items)
        str_missing_cop_files += (f"* {file_name}\n")

    if _check_only_file_mode and _DEFAULT_EXCLUDE_EXTENSION_FILES is not None and len(
            _DEFAULT_EXCLUDE_EXTENSION_FILES) > 0:
        logger.info("# FILES EXCLUDED - NOT SUBJECT TO REUSE")
        logger.info('* %s' % '\n* '.join(map(str, _DEFAULT_EXCLUDE_EXTENSION_FILES)))
        logger.info("\n" + _MSG_REFERENCE)
    else:
        if print_mode and files_without_license is not None and len(files_without_license) > 0:
            message = "# MISSING LICENSES FROM FILE LIST TO CHECK\n" + str_missing_lic_files + "\n"
        if print_mode and files_without_copyright is not None and len(files_without_copyright) > 0:
            message += "# MISSING COPYRIGHT FROM FILE LIST TO CHECK\n" + str_missing_cop_files + "\n"

    return message


def write_result_xml(result_file: str, exit_code: int) -> None:
    # Create a new XML file with the results
    try:
        output_dir = os.path.dirname(result_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        ET.ElementTree(_root_xml_item).write(result_file, encoding="UTF-8", xml_declaration=True)
        error_items = ET.ElementTree(_root_xml_item).findall('system_error')
        if len(error_items) > 0:
            logger.warning("# SYSTEM ERRORS")
            for xml_item in error_items:
                logger.warning(xml_item.text)
    except Exception as ex:
        logger.error(f"Error_to_write_xml: {ex}")
        exit_code = os.EX_IOERR
    try:
        _str_final_result_log = safe_dump(_result_log, allow_unicode=True, sort_keys=True)
        logger.info(_str_final_result_log)
    except Exception as ex:
        logger.warning(f"Failed to print result log. {ex}")
    return exit_code


def write_result_html(result_file: str, exit_code: int) -> None:
    try:
        logger.warning(f"write_result_html : {result_file}")
    except Exception as ex:
        logger.error(f"Error_to_write_html: {ex}")
        exit_code = os.EX_IOERR
    return exit_code


def write_result_yaml(result_file: str, exit_code: int) -> None:
    try:
        logger.warning(f"write_result_yaml : {result_file}")
    except Exception as ex:
        logger.error(f"Error_to_write_yaml: {ex}")
        exit_code = os.EX_IOERR
    return exit_code


def init(path_to_find, output_file_name, file_list):
    global logger, _start_time, _result_log

    _start_time = datetime.now().strftime('%Y%m%d_%H-%M-%S')
    output_dir = os.path.dirname(os.path.abspath(output_file_name))
    logger, _result_log = init_log(os.path.join(output_dir, f"fosslight_reuse_log_{_start_time}.txt"),
                                   True, logging.INFO, logging.DEBUG, _PKG_NAME, path_to_find)
    if file_list:
        _result_log["File list to check"] = file_list


def create_result_file(output_file_name, format):
    success, msg, output_path, output_file, output_extension = check_output_format(output_file_name, format, _CUSTOMIZED_FORMAT_FOR_REUSE)
    if success:
        result_file = ""
        if output_path == "":
            output_path = os.getcwd()
        else:
            output_path = os.path.abspath(output_path)

        if output_file != "":
            result_file = output_file
        else:
            if output_extension == '.xml':
                result_file = f"FOSSLight_Reuse_{_start_time}.xml"
            elif output_extension == '.html':
                result_file = f"FOSSLight_Reuse_{_start_time}.html"
            elif output_extension == '.yaml':
                result_file = f"FOSSLight_Resue_{_start_time}.yaml"
            else:
                # todo: All file?
                result_file = f"FOSSLight_Reuse_{_start_time}.xml"

        result_file = os.path.join(output_path, result_file)
    else:
        logger.error(f"Format error - {msg}")
        sys.exit(1)

    return result_file


def write_result_file(result_file, format, exit_code):
    if format == "" or format == "xml":
        exit_code = write_result_xml(result_file, exit_code)
    elif format == "html":
        exit_code = write_result_html(result_file, exit_code)
    elif format == "yaml":
        exit_code = write_result_yaml(result_file, exit_code)
    else:
        logger.info("Not supported file extension")
    sys.exit(exit_code)


def get_path_to_find(target_path, _check_only_file_mode):
    is_file = False
    is_folder = False
    file_to_check_list = []
    path_list = []

    path_list = target_path.split(',')

    # Check if all elements are only files or folder
    for path in path_list:
        if os.path.isdir(path) and not is_folder:
            is_folder = True
            if path == "":
                path_to_find = os.getcwd()
            else:
                path_to_find = os.path.abspath(path)
        elif os.path.isfile(path):
            is_file = True
            path_to_find = os.getcwd()

    if is_file & is_folder:
        logger.error("Input only a folder or files with -p option")
    elif not is_folder and not is_file:
        file_to_check_list = path_list
        _check_only_file_mode = True

    return path_to_find, file_to_check_list, _check_only_file_mode


def run_lint(target_path, format, disable, output_file_name):
    global _turn_on_default_reuse_config, _check_only_file_mode

    file_to_check_list = []
    _exit_code = os.EX_OK
    path_to_find = ""

    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except Exception as ex:
        print_error(f"Error - locale : {ex}")

    path_to_find, file_to_check_list, _check_only_file_mode = get_path_to_find(target_path, _check_only_file_mode)

    init(path_to_find, output_file_name, file_to_check_list)
    result_file = create_result_file(output_file_name, format)

    _turn_on_default_reuse_config = not disable

    if _check_only_file_mode:
        license_missing_files, copyright_missing_files, error_occurred, project = reuse_for_files(path_to_find, file_to_check_list)
        oss_pkg_info = []
    else:
        str_lint_result, license_missing_files, copyright_missing_files, oss_pkg_info, error_occurred, project \
            = reuse_for_project(path_to_find)

    if error_occurred:  # In case reuse lint failed
        _exit_code = os.EX_SOFTWARE
    else:
        msg_missing_files = result_for_missing_license_and_copyright_files(license_missing_files, copyright_missing_files, oss_pkg_info)
        if not _check_only_file_mode:
            result_for_summary(str_lint_result,
                               oss_pkg_info,
                               path_to_find,
                               msg_missing_files)

    write_result_file(result_file, format, _exit_code)

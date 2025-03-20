#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only
import os
import urllib.request
import logging
import fosslight_util.constant as constant
import shutil
from pathlib import Path
from askalono import identify
from bs4 import BeautifulSoup
from reuse.project import Project
from reuse.download import run as reuse_download
from fosslight_util.parsing_yaml import find_sbom_yaml_files, parsing_yml
from fosslight_prechecker._add_header import reuse_parser
from fosslight_prechecker._add import check_input_license_format, get_spdx_license_list, spdx_licenses
from fosslight_prechecker._precheck import dump_error_msg, get_path_to_find


OPENSOURCE_LGE_COM_URL_PREFIX = "https://opensource.lge.com/license/"
LICENSE_INCLUDE_FILES = ["license", "license.md", "license.txt", "notice"]
ASKALONO_THRESHOLD = 0.7

logger = logging.getLogger(constant.LOGGER_NAME)


def download_license(target_path: str, input_license: str) -> None:
    _check_only_file_mode = False
    path_to_find, _, _check_only_file_mode = get_path_to_find(target_path, _check_only_file_mode)

    get_spdx_license_list()

    # Find and create representative license file
    if input_license:
        find_representative_license(path_to_find, input_license)
    else:
        # Download license text file of OSS-pkg-info.yaml
        download_oss_info_license(path_to_find)

def lge_lic_download(temp_download_path: str, input_license: str) -> bool:
    success = False

    input_license_url = input_license.replace(' ', '_').replace('/', '_').replace('LicenseRef-', '').replace('-', '_')
    lic_url = OPENSOURCE_LGE_COM_URL_PREFIX + input_license_url + ".html"

    try:
        html = urllib.request.urlopen(lic_url)
        source = html.read()
        html.close()
    except urllib.error.URLError:
        logger.error("Invalid URL address")
    except ValueError as val_err:
        logger.error(f"Invalid Value : {val_err}")
    except Exception as ex:
        logger.error(f"Error to open url - {lic_url} : {ex}")

    soup = BeautifulSoup(source, 'html.parser')
    try:
        lic_text = soup.find("p", "bdTop")
        Path(os.path.join(temp_download_path, 'LICENSES')).mkdir(parents=True, exist_ok=True)
        lic_file_path = os.path.join(temp_download_path, 'LICENSES', f'{input_license}.txt')

        with open(lic_file_path, 'w', encoding='utf-8') as f:
            f.write(lic_text.get_text(separator='\n'))
        if os.path.isfile(lic_file_path):
            logger.info(f"Successfully downloaded {lic_file_path}")
            success = True
    except Exception as ex:
        logger.error(f"Error to download license from LGE : {ex}")
    return success


def present_license_file(path_to_check: str, lic: str) -> bool:
    present = False
    lic_file_path = os.path.join(path_to_check, 'LICENSES')
    file_name = f"{lic}.txt"
    if file_name in os.listdir(lic_file_path):
        present = True
    return present


def download_oss_info_license(base_path: str = "") -> None:
    license_list = []
    converted_lic_list = []
    oss_yaml_files = []
    main_parser = reuse_parser()
    prj = Project(base_path)

    oss_yaml_files = find_sbom_yaml_files(base_path)

    if oss_yaml_files is None or len(oss_yaml_files) == 0:
        logger.info("\n # There is no OSS package Info file in this path\n")
        return
    else:
        logger.info(f"\n # There is OSS Package Info file(s) : {oss_yaml_files}\n")

    for oss_pkg_file in oss_yaml_files:
        _, license_list, _ = parsing_yml(oss_pkg_file, base_path)

    for lic in license_list:
        converted_lic_list.append(check_input_license_format(lic))

    if license_list is not None and len(license_list) > 0:
        parsed_args = main_parser.parse_args(['download'] + converted_lic_list)

        try:
            reuse_download(parsed_args, prj)
        except Exception as ex:
            dump_error_msg(f"Error - download license text in OSS-pkg-info.yml : {ex}")
    else:
        logger.info(" # There is no license in the path \n")

    return converted_lic_list


def copy_to_root(path_to_find: str, input_license: str, temp_download_path: str) -> None:
    lic_file = f"{input_license}.txt"
    try:
        source = os.path.join(temp_download_path, 'LICENSES', f'{lic_file}')
        destination = os.path.join(path_to_find, 'LICENSE')
        shutil.copyfile(source, destination)
        logger.warning(f"# Created Representative License File ({source} -> LICENSE)\n")
        shutil.rmtree(temp_download_path)
    except Exception as ex:
        dump_error_msg(f"Error - Can't copy license file: {ex}")


def check_license_name(license_txt, is_filepath=False):
    license_name = ''
    if is_filepath:
        with open(license_txt, 'r', encoding='utf-8') as f:
            license_content = f.read()
    else:
        license_content = license_txt

    detect_askalono = identify(license_content)
    if detect_askalono.score > ASKALONO_THRESHOLD:
        license_name = detect_askalono.name
    return license_name


def find_representative_license(path_to_find: str, input_license: str) -> None:
    files = []
    found_file = []
    found_license_file = False
    main_parser = reuse_parser()
    reuse_return_code = 0
    success_from_lge = False
    present_lic = False

    all_items = os.listdir(path_to_find)
    for item in all_items:
        if os.path.isfile(item):
            files.append(os.path.basename(item))

    for file in files:
        file_lower_case = file.lower()
        if file_lower_case in LICENSE_INCLUDE_FILES or file_lower_case.startswith("license") or file_lower_case.startswith("notice"):
            found_file.append(file)
            found_license_file = True

    input_license = check_input_license_format(input_license)
    logger.info(f"\n - Input license to be representative: {input_license}")

    input_license = input_license.replace(os.path.sep, '')
    try:
        if found_license_file:
            for lic_file in found_file:
                found_license = check_license_name(os.path.abspath(lic_file), True)
                logger.warning(f"# Already exists representative license file: {found_license}, path: {os.path.abspath(lic_file)}\n")
        else:
            temp_download_path = os.path.join(path_to_find, "temp_lic")
            os.makedirs(temp_download_path, exist_ok=True)
            prj = Project(temp_download_path)
            parsed_args = main_parser.parse_args(['download', f"{input_license}"])

            # 0: successfully downloaded, 1: failed to download
            reuse_return_code = reuse_download(parsed_args, prj)
            # Check if the license text file is present
            present_lic = present_license_file(temp_download_path, input_license)

            if reuse_return_code == 1 and not present_lic:
                # True : successfully downloaded from LGE
                success_from_lge = lge_lic_download(temp_download_path, input_license)
                if success_from_lge:
                    logger.warning(f"\n# Successfully downloaded from LGE")
            
            if reuse_return_code == 0 or success_from_lge:
                copy_to_root(path_to_find, input_license, temp_download_path)
    except Exception as ex:
        dump_error_msg(f"Error - download representative license text: {ex}")
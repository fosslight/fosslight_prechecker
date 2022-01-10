#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: GPL-3.0-only

import logging
from fosslight_util.constant import LOGGER_NAME

_logger = logging.getLogger(LOGGER_NAME)


class OssItem:
    name = "-"
    version = ""
    licenses = []
    source = ""
    files = []
    copyright = ""
    comment = ""
    exclude = ""
    homepage = ""
    relative_path = ""

    def __init__(self, value):
        self.name = "-"
        self.version = ""
        self.licenses = []
        self.source = ""
        self.files = []
        self.copyright = ""
        self.comment = ""
        self.exclude = ""
        self.homepage = ""
        self.relative_path = value

    def __del__(self):
        pass

    def set_homepage(self, value):
        self.homepage = value

    def set_comment(self, value):
        self.comment = value

    def set_copyright(self, value):
        if value != "":
            if isinstance(value, list):
                value = "\n".join(value)
            value = value.strip()
        self.copyright = value

    def set_exclude(self, value):
        if value:
            self.exclude = "Exclude"
        else:
            self.exclude = ""

    def set_name(self, value):
        self.name = value

    def set_version(self, value):
        self.version = str(value)

    def set_licenses(self, value):
        if not isinstance(value, list):
            value = value.split(",")
        self.licenses.extend(value)
        self.licenses = [item.strip() for item in self.licenses]
        self.licenses = list(set(self.licenses))

    def set_files(self, value):
        if isinstance(value, list):
            self.files.extend(value)
        else:
            self.files.append(value)
        self.files = list(set(self.files))

    def set_source(self, value):
        self.source = value

    def get_print_array(self):
        items = []
        if len(self.files) == 0:
            self.files.append("")
        if len(self.licenses) == 0:
            self.licenses.append("")
        for file in self.files:
            lic = ",".join(self.licenses)
            if self.relative_path != "" and not str(self.relative_path).endswith("/"):
                self.relative_path += "/"
            items.append([self.relative_path + file, self.name, self.version, lic, self.source, self.homepage,
                          self.copyright, "", self.exclude, self.comment])
        return items

    def get_print_json(self):
        json_item = {}
        json_item["name"] = self.name

        if self.version != "":
            json_item["version"] = self.version
        if self.source != "":
            json_item["source"] = self.source
        if self.copyright != "":
            json_item["copyright"] = self.copyright
        if self.exclude != "":
            json_item["exclude"] = self.exclude
        if self.comment != "":
            json_item["comment"] = self.comment
        if self.homepage != "":
            json_item["homepage"] = self.homepage

        if len(self.files) > 0:
            json_item["file"] = self.files
        if len(self.licenses) > 0:
            json_item["license"] = self.licenses

        return json_item


def invalid(cmd):
    _logger.info('[{}] is invalid'.format(cmd))

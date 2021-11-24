<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: GPL-3.0-only
 -->
# FOSSLight Reuse

<img src="https://img.shields.io/pypi/l/fosslight-reuse" alt="License" /> <img src="https://img.shields.io/pypi/v/fosslight_reuse" alt="Current python package version." /> <img src="https://img.shields.io/pypi/pyversions/fosslight_reuse" /> [![REUSE status](https://api.reuse.software/badge/github.com/fosslight/fosslight_reuse)](https://api.reuse.software/info/github.com/fosslight/fosslight_reuse)

**FOSSLight Reuse** is a tool that can be used to comply with the copyright/license writing rules in the source code.     
It uses [reuse-tool][ret] to check whether the [source code's copyright and license writing rules][rule] are complied with.

[ret]: https://github.com/fsfe/reuse-tool
[rule]: https://oss.lge.com/guide/process/osc_process/1-identification/copyright_license_rule.html


## 📖 User Guide
Please see the [**User Guide**](https://fosslight.org/fosslight-guide-en/scanner/1_reuse.html) for more information on how to install and run it.    
Here a short summary:    

- `lint` --- Check whether the [source code's copyright and license writing rules][rule] are complied with.

- `convert` --- Convert [oss-pkg-info.yaml](https://github.com/fosslight/fosslight_reuse/blob/main/tests/convert/oss-pkg-info.yaml) to [FOSSLight-Report.xlsx](https://fosslight.org/fosslight-guide-en/learn/2_fosslight_report.html) and vice versa.

- `add` --- Add copyright and license to missing file(s)


## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [Git Repository][repo]. Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[repo]: https://github.com/fosslight/fosslight_reuse/issues

## 📄 License  
FOSSLight Reuse is licensed under [GPL-3.0-only][l].

[l]: https://github.com/fosslight/fosslight_reuse/blob/main/LICENSE

<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: GPL-3.0-only
 -->
# FOSSLight Prechecker

<img src="https://img.shields.io/pypi/l/fosslight-prechecker" alt="License" /> <img src="https://img.shields.io/pypi/v/fosslight_prechecker" alt="Current python package version." /> <img src="https://img.shields.io/pypi/pyversions/fosslight_prechecker" /> [![REUSE status](https://api.reuse.software/badge/github.com/fosslight/fosslight_prechecker)](https://api.reuse.software/info/github.com/fosslight/fosslight_prechecker)

**FOSSLight Prechecker** is a tool that can be used to comply with the copyright/license writing rules in the source code.     
It uses [reuse-tool][ret] to check whether the [source code's copyright and license writing rules][rule] are complied with.

[ret]: https://github.com/fsfe/reuse-tool
[rule]: https://opensource.lge.com/guide/19

## 📖 User Guide
Please see the [**User Guide**](https://fosslight.org/fosslight-guide-en/scanner/1_prechecker.html) for more information on how to install and run it.    
Here a short summary:    

- `lint` --- (Default) Check whether the [source code's copyright and license writing rules][rule] are complied with.

- `convert` --- Convert [sbom-info.yaml](https://github.com/fosslight/fosslight_prechecker/blob/main/tests/convert/sbom-info.yaml) or [oss-pkg-info.yaml](https://github.com/fosslight/fosslight_prechecker/blob/main/tests/convert/oss-pkg-info.yaml) to [fosslight_report.xlsx](https://fosslight.org/fosslight-guide-en/learn/2_fosslight_report.html).

- `add` --- Add copyright and license to missing file(s)


## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [Git Repository][repo]. Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[repo]: https://github.com/fosslight/fosslight_prechecker/issues

## 📄 License  
FOSSLight Prechecker is licensed under [GPL-3.0-only][l].

[l]: https://github.com/fosslight/fosslight_prechecker/blob/main/LICENSE

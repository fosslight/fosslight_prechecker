# Changelog

## v3.0.15 (02/02/2023)
## Changes
## 🐛 Hotfixes

- Fix bug about contents of xml result @bjk7119 (#137)

---

## v3.0.14 (30/01/2023)
## Changes
## 🐛 Hotfixes

- Bug fix to encode html result file @bjk7119 (#136)

---

## v3.0.13 (27/01/2023)
## Changes
## 🐛 Hotfixes

- Add git ignore option(-c) for excluding @bjk7119 (#135)

## 🔧 Maintenance

- Unify version output format @bjk7119 (#133)
- Change package to get release package @bjk7119 (#132)
- Update version of packages for actions @bjk7119 (#131)
- Modify typo of example of convert @bjk7119 (#130)

---

## v3.0.12 (02/01/2023)
## Changes
## 🐛 Hotfixes

- Bug fix not to print no ext. file name @bjk7119 (#128)
- Modify to print file wo ext. correctly @bjk7119 (#124)
- Fix yaml file encoding error @bjk7119 (#120)

## 🔧 Maintenance

- Modify typo of example of convert @bjk7119 (#130)
- Modify to check file extension efficiently @bjk7119 (#129)
- Download license file regardless of representative license @bjk7119 (#127)
- Remove frequent license nick list file @bjk7119 (#126)
- Modify to match SPDX regardless of case @bjk7119 (#125)
- Modify to simplify file list in OSS_PKG_FILES @bjk7119 (#123)
- Add *sbom_info*.yaml pattern to OSS_PKG_INFO_FILES @bjk7119 (#122)

---

## v3.0.11 (18/11/2022)
## Changes
## 🚀 Features

- Modify to run all mode on Windows @bjk7119 (#117)
- Exclude untracked files and ignored files in lint mode @bjk7119 (#113)

## 🐛 Hotfixes

- Fix yaml file encoding error @bjk7119 (#120)
- Replace windows operator to '/' for path in yaml @soimkim (#119)
- Fix Dep5 encoding error @soimkim (#118)

## 🔧 Maintenance

- Add tox configuration for Windows @bjk7119 (#116)
- Modify downloading the license text @bjk7119 (#115)
- Exclude untracked files in input path @bjk7119 (#114)

---

## v3.0.10 (04/11/2022)
## Changes
## 🐛 Hotfixes

- Fix bug for not working options(-n, i) @bjk7119 (#111)
- Set lint mode to default mode. @bjk7119 (#111)
- Not print progress bar in add mode when interactive working @bjk7119 (#111)

## 🔧 Maintenance

- Print license text through notice parameter @dd-jy (#112)

---

## v3.0.9 (19/10/2022)
## Changes
## 🐛 Hotfixes

- Fix bug that doesn't work -v, -h option @bjk7119 (#110)

---

## v3.0.8 (12/10/2022)
## Changes
## 🐛 Hotfixes

- Fix bug in lint and add error for Windows @bjk7119 (#109)

## 🔧 Maintenance

- Add OSS pkg file list for Nuget @bjk7119 (#108)

---

## v3.0.7 (06/10/2022)
## Changes
## 🚀 Features

- Convert multiple yaml files into one report @bjk7119 (#107)

---

## v3.0.6 (15/09/2022)
## Changes
## 🔧 Maintenance

- Modify result file name format @bjk7119 (#106)

---

## v3.0.5 (15/09/2022)
## Changes
## 🔧 Maintenance

- Fix to print argparse help msg if input no mode @bjk7119 (#104)

---

## v3.0.4 (01/09/2022)
## Changes
## 🐛 Hotfixes

- Fix not to print argparse's help msg @bjk7119 (#102)
- Fix bug where path in sbom-info.yaml is not excluded from lint result @bjk7119 (#101)

## 🔧 Maintenance

- Apply new help msg if invalid input @bjk7119 (#103)

---

## v3.0.3 (19/08/2022)
## Changes
## 🐛 Hotfixes

- Change the exit code to a constant for windows @soimkim (#99)

---

## v3.0.2 (12/08/2022)
## Changes
## 🔧 Maintenance

- Remove the function to convert excel to yaml @bjk7119 (#98)
- Remove unnecessary code @bjk7119 (#97)
- Run current path if no input path @bjk7119 (#96)
- Remove the code of filtering fille name in convert mode @bjk7119 (#95)
- Delete unnecessary returns @soimkim (#94)
- Add new format of oss-pkg-info.yaml @bjk7119 (#93)
- Change the message if there is nothing to convert @soimkim (#92)
- Modify badge info in README.md @bjk7119 (#90)

---

## v3.0.1 (22/07/2022)
## Changes
## 🐛 Hotfixes

- Remove unused packages @bjk7119 (#89)

---

## v3.0.0 (22/07/2022)
## Changes
## 🔧 Maintenance

- Rename FOSSLight Reuse to FOSSLight Prechecker @bjk7119 (#87)

---

## v2.2.2 (20/07/2022)
## Changes
## 🔧 Maintenance

- Add -v option and error handling in convert mode @bjk7119 (#85)
- Move read excel code to FL Util @bjk7119 (#84)
- Apply fnmatch / re match to match file name @bjk7119 (#83)
- Remove scroll from html @soimkim (#79)
- Change it to a responsive table @soimkim (#78)
- Remove gray background from html @soimkim (#77)
- Modify html format when files exceeds 100 @bjk7119 (#76)

---

## v2.2.1 (28/06/2022)
## Changes
## 🚀 Features

- Add generating html format file @bjk7119 (#73)

## 🔧 Maintenance

- Add expand button in html @bjk7119 (#75)
- Add execution error handling for html @bjk7119 (#74)
- Change field's name in yaml file @bjk7119 (#72)

---

## v2.2.0 (16/06/2022)
## Changes
## 🚀 Features

- Make the sheet to convert selectable. (-s sheet name option) @soimkim (#65)
- Add the i (--ignore) option to not create a log file. @soimkim (#64)
- Add creating xml result file @bjk7119 (#53)
- Add code of creating yaml result file @bjk7119 (#52)
- Change -p, -f option @bjk7119 (#51)

## 🐛 Hotfixes

- Fix the bug that Excel cannot be created if there is only one row in Convert mode @soimkim (#58)

## 🔧 Maintenance

- Change path to analyze path to print in lint mode @bjk7119 (#71)
- Find sheet names without case sensitivity @soimkim (#70)
- Exclude for sbom info yaml file in Lint mode @bjk7119 (#68)
- update the minimum version of fosslight_util @bjk7119 (#67)
- Modification for compliance with pep8 @bjk7119 (#66)
- Exclude for open source package file in w/o list @bjk7119 (#63)
- Apply -o option in add mode @bjk7119 (#62)
- Check compliant except for files for which Exclude is True @soimkim (#61)
- Remove duplicate files in w/o license or copyright list @bjk7119 (#60)
- Load SRC, BIN Sheet in excel @soimkim (#59)
- Apply changed parsing_yaml return value @bjk7119 (#57)
- Apply parsing and convert new yaml format @bjk7119 (#56)
- Add excution error result @bjk7119 (#55)
- Modify function of converting excel to yaml @bjk7119 (#54)
- Remove yaml parsing code @bjk7119 (#48)
- Add a commit message checker @soimkim (#47)

---

## v2.1.9 (11/03/2022)
## Changes
## 🔧 Maintenance

- Change appending list in for loop to using yield @bjk7119 (#46)
- Apply f-string format @bjk7119 (#45)

---

## v2.1.8 (24/02/2022)
## Changes
## 🔧 Maintenance

- Comment out some sentences in the PR template @soimkim (#44)
- Fix to print help message if don't write mode @bjk7119 (#43)

---

## v2.1.7 (17/01/2022)
## Changes
## 🔧 Maintenance
* When converting Yaml, modify it so that Copyright can be read as a list.

---

## v2.1.6 (19/11/2021)
## Changes
## 🔧 Maintenance

- Add sheet name(BIN(Yocto)) to use Yocto report @bjk7119 (#42)

---

## v2.1.5 (17/11/2021)
## Changes
## 🐛 Hotfixes

- Bug fix to create .xlsx file @bjk7119 (#40)

---

## v2.1.4 (07/11/2021)
## Changes
## 🚀 Features

- Add code of downloading license text @bjk7119 (#38)

---

## v2.1.3 (21/10/2021)
## Changes
## 🔧 Maintenance

- Change mode name : report -> convert @bjk7119 (#35)

---

## v2.1.2 (19/10/2021)
## Changes
## 🐛 Hotfixes

- Bug fix to use with abspath and relpath @bjk7119 (#34)

## 🔧 Maintenance

- Use python-debian v0.1.40 @bjk7119 (#34)

---

## v2.1.1 (12/10/2021)
## Changes
## 🐛 Hotfixes

- Fix to Flake8 v4.0.0 bug -> using v3.9.2 (when using tox) @bjk7119 (#33)

## 🔧 Maintenance

- Modify to print help message one time @bjk7119 (#33)
- Modify to test add mode @bjk7119 (#32)

---

## v2.1.0 (16/09/2021)
## Changes
## 🚀 Features

- Apply add mode to add license and copyright @bjk7119 (#30)

## 🔧 Maintenance

- Delete -m option @bjk7119 (#31)

---

## v2.0.3 (26/08/2021)
## Changes
## 🐛 Hotfixes

- Fix a bug related release action @soimkim (#24)

## 🔧 Maintenance

- Set condition to use FOSSLight Util v1.1.0 or later @bjk7119 (#16)

# Changelog

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

---

## v2.0.2 (12/08/2021)
## Changes
## 🔧 Maintenance

- Merge init_log & init_log_item functiions @bjk7119 (#15)

---

## v2.0.1 (29/07/2021)
## Changes
## 🐛 Hotfixes

- Bug fix to checkout new version @bjk7119 (#13)

## 🔧 Maintenance

- Remove waring in publish-release.yml @bjk7119 (#12)
- Update version in setup.py when release @soimkim (#11)

---

## v2.0.0 (22/07/2021)

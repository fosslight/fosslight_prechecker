<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: Apache-2.0
 -->
# FOSSLight REUSE
```note
Tool to check REUSE compliance in source code by using reuse-tool.
```

**FOSSLight REUSE** uses [reuse-tool][ret], to detect the copyright and license phrases contained in the file. Some files (ex- build script), binary files, directory and files in specific directories (ex-test) are excluded from the result. And removes words such as "-only" and "-old-style" from the license name to be printed. The output result is generated in Excel format.


[ret]: https://github.com/fsfe/reuse-tool

## 🎉 How to install

It can be installed using pip3.     
It is recommended to install it in the [python 3.6 + virtualenv](https://github.com/fosslight/fosslight_source/blob/main/docs/Guide_virtualenv.md) environment.

```
$ pip3 install fosslight_reuse
```

## 🚀 How to run
``` 
$ fosslight_reuse 
```
### Parameters      
| Parameter  | Argument | Required  | Description |
| ------------- | ------------- | ------------- |------------- |
| p | [root_path_to_check] | O | Source path to check. | 
| h | None | X | Print help message. | 
| n | None | X | Add this parameter if you do not want to exclude venv*, node_modules, and .*/ from the analysis.|    
| r | [result_file_name] | X | xml format result file name. (Default: reuse_checker.xml) |    
| f | [file1,file2,...] | X | List of files to check copyright and license. |

### Ex 1. Run with minimal parameters 
``` 
$ fosslight_reuse -p [root_path_to_check]
```
### Ex 2. Check for specific files
Copyright text and License text are printed for /home/test/notice/sample.py, /home/test/src/init.py.
```
$ fosslight_reuse -p /home/test/ -f "notice/sample.py,src/init.py"
```
## How it works
1. Check if it exists in the directory received by parameter -p.
2. Find a OSS Package Information file.
3. Run a Reuse lint.    
    3-1. When running on a project basis. (without -f parameter)
    - If there is no ./reuse/dep5 file in the Root Path, it is created.
    - If it already exists, copy it to bk file and append the default config value to the existing dep file.
    - By creating dep5 files, exclude binary or .json, venv */*, node_modules/*,. */* from reuse.
    - Run the reuse lint 
        If the OSS Package Information file exists, the list of missing license files is not printed.
    - Rollback dep5-related file creation part.    
    
    3-2. When executing in file unit (with -f option)
    - Print the copyright text and license text extraction by file.
    - However, if the file does not exist or the file is binary or .json, copyright text and license text are not printed.

4. Print the execution result and save it in xml format.

## 📁 Result
### Ex 1. Analyze the files in path.
```
(venv)$ fosslight_reuse -p /home/test/reuse-example -r result.xml
```
```
# SUMMARY
# Open Source Package info: File to which OSS Package information is written.
# Used licenses: License detected in the path.
# Files with copyright information: Number of files with copyright / Total number of files.
# Files with license information: Number of files with license / Total number of files.
 
* Open Source Package info: /home/test/reuse-example/oss-package.info
* Used licenses: CC-BY-4.0, CC0-1.0, GPL-3.0-or-later
* Files with copyright information: 6 / 7
* Files with license information: 6 / 7

```

### Ex 2. Analyze specific files. 
The detected License and Copyright information for each file is output.
```
(venv)$ fosslight_reuse  -p /home/soimkim/test/reuse-example -f "src/load.c,src/dummy.c,src/main.c"
```
```
# src/load.c
* License:
* Copyright: SPDX-FileCopyrightText: 2019 Jane Doe <jane@example.com>
 
# src/dummy.c
* License:
* Copyright:
 
# src/main.c
* License: GPL-3.0-or-later
* Copyright: SPDX-FileCopyrightText: 2019 Jane Doe <jane@example.com>

```

## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [Git Repository][repo]. Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[repo]: https://github.com/fosslight/fosslight_reuse/issues

## 📄 License
Copyright (c) 2020 LG Electronics, Inc. 
FOSSLight REUSE is Apache-2.0, as found in the [LICENSE][l] file.

[l]: https://github.com/fosslight/fosslight_reuse/blob/main/LICENSE

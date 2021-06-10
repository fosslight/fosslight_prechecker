<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: Apache-2.0
 -->
# FOSSLight REUSE
```note
Tool to check REUSE compliance in source code by using reuse-tool.
```

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
| n | None | X | If you do not want to use the Default REUSE dep5 file, add this parameter. Default REUSE dep5 file function: exclude venv*/, node_modules,.*/ Folders, .json and binary file from reuse lint.) |    
| r | [result_file_name] | X | File name to save the result in xml format. (Default : reuse_checker.xml ) |    
| f | [file_list] | X | List of files to check if license information is not included.  (Separator : ,) |

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


## 📁 Result

```
$ tree
.
├── OSS-Report_2021-05-03_00-39-49.csv
├── OSS-Report_2021-05-03_00-39-49.xlsx
├── scancode_2021-05-03_00-39-49.json
└── fosslight_src_log_2021-05-03_00-39-49.txt

```

## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [Git Repository][repo]. Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[repo]: https://github.com/fosslight/fosslight_reuse/issues

## 📄 License
Copyright (c) 2020 LG Electronics, Inc. 
FOSSLight REUSE is Apache-2.0, as found in the [LICENSE][l] file.

[l]: https://github.com/fosslight/fosslight_reuse/blob/main/LICENSE

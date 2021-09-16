# SPDX-License-Identifier: GPL-3.0-only

import os
from fosslight_util.set_log import init_log


def main():
    output_dir = "tests"
    logger, _result_log = init_log(os.path.join(output_dir, "test_add_log.txt"))
    logger.warning("TESTING - add mode")


if __name__ == '__main__':
    main()

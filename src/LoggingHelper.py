"""
    File name: LoggingHelper.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 10/12/2020
    Python Version: 3.8
"""

from src.ConfigHelper import ConfigHelper

import datetime


class LoggingHelper:
    @staticmethod
    def log(msg, end="\n"):
        if ConfigHelper.get_print_timestamp():
            log_msg = "{}\t{}".format(datetime.datetime.now(), msg)
        else:
            log_msg = msg
        print(log_msg, end=end, flush=True)

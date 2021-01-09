"""
    File name: ZoneState.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 09/01/2021
    Python Version: 3.8
"""

from enum import Enum


class ZoneState(Enum):
    OFF = 0
    ON = 1
    DEEP_SLEEP = 2

    @staticmethod
    def invert(val):
        if val == ZoneState.ON:
            return ZoneState.OFF
        return ZoneState.ON


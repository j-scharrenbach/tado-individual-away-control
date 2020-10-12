"""
    File name: ClientState.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 10/12/2020
    Python Version: 3.8
"""

from enum import Enum


class ClientState(Enum):
    UNKNOWN = 0
    HOME = 1
    AWAY = 2

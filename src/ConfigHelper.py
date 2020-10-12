"""
    File name: ConfigHelper.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 10/12/2020
    Python Version: 3.8
"""

import json


class ConfigHelper:
    CONFIG = None

    @staticmethod
    def initialize():
        if ConfigHelper.CONFIG is None:
            with open("config.json") as f:
                ConfigHelper.CONFIG = json.load(f)

    @staticmethod
    def get_credentials():
        return ConfigHelper.CONFIG["username"], ConfigHelper.CONFIG["password"]

    @staticmethod
    def get_ips():
        ips = set()

        for r in ConfigHelper.CONFIG["rules"]:
            for ip in r["ips"]:
                ips.add(ip)

        return list(ips)

    @staticmethod
    def get_rules():
        return ConfigHelper.CONFIG["rules"]

    @staticmethod
    def get_interval():
        return int(ConfigHelper.CONFIG["interval"])

    @staticmethod
    def get_zones():
        return set(r["zone_id"] for r in ConfigHelper.CONFIG["rules"])

    @staticmethod
    def get_max_ping_cnt():
        return int(ConfigHelper.CONFIG["max_ping_cnt"])

    @staticmethod
    def get_away_temperature():
        return int(ConfigHelper.CONFIG["away_temperature"])

    @staticmethod
    def get_client_state_history_len():
        return int(ConfigHelper.CONFIG["client_state_history_len"])

    @staticmethod
    def get_min_home_success_pings():
        return int(ConfigHelper.CONFIG["min_home_success_pings"])

    @staticmethod
    def get_print_timestamp():
        return ConfigHelper.CONFIG["print_timestamp"]

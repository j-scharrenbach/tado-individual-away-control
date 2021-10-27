"""
    File name: ConfigHelper.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 06/10/2021
    Python Version: 3.8
"""

import json
import os
import sys
import copy

class ConfigHelper:
    __CONFIG = None

    __RULES = None
    __ZONES = None
    __DEVICES = None

    MIN_INTERVAL = 15

    @staticmethod
    def initialize():
        if ConfigHelper.__CONFIG is None:
            with open(os.path.dirname(__file__) + "/" + os.path.pardir + "/config.json") as f:
                ConfigHelper.__CONFIG = json.load(f)

    @staticmethod
    def initialize_zones(zones):
        ConfigHelper.__ZONES = zones
        ConfigHelper.get_zones()

    @staticmethod
    def get_credentials():
        return ConfigHelper.__CONFIG["username"], ConfigHelper.__CONFIG["password"]

    @staticmethod
    def get_default_stale_state():
        return ConfigHelper.__CONFIG["default_stale_state"]

    @staticmethod
    def get_devices():
        if not ConfigHelper.__DEVICES:
            devices = set()
            for r in ConfigHelper.get_rules():
                for d in r["device"]:
                    devices.add(d)

            ConfigHelper.__DEVICES = list(devices)
        return ConfigHelper.__DEVICES

    @staticmethod
    def get_rules():
        if ConfigHelper.__RULES is None:
            # initially construct rules
            ConfigHelper.__RULES = list()
            def_rule = None

            for r in ConfigHelper.__CONFIG["rules"]:
                if isinstance(r["zone_id"], list):
                    # create rule for each element
                    for z in r["zone_id"]:
                        r_copy = copy.copy(r)
                        r_copy["zone_id"] = z
                        ConfigHelper.__RULES.append(r_copy)
                elif not isinstance(r["zone_id"], str):
                    # save rule
                    ConfigHelper.__RULES.append(r)
                elif r["zone_id"] == "default":
                    # set default rule
                    def_rule = r

            if def_rule is not None and ConfigHelper.__ZONES is not None:
                # generate default rule
                default_zones = set(t_zone["id"] for t_zone in ConfigHelper.__ZONES).difference(set(z_defined["zone_id"] for z_defined in ConfigHelper.__RULES))
                for z in default_zones:
                    r_copy = copy.copy(def_rule)
                    r_copy["zone_id"] = z
                    ConfigHelper.__RULES.append(r_copy)

            # check validity
            z_ids = set()
            for r in ConfigHelper.__RULES:
                if r["zone_id"] in z_ids:
                    print("Invalid config, multiple rules for zone {}!".format(r["zone_id"]))
                    sys.exit(1)
                else:
                    z_ids.add(r["zone_id"])

        return ConfigHelper.__RULES

    @staticmethod
    def get_interval():
        return max(ConfigHelper.MIN_INTERVAL, int(ConfigHelper.__CONFIG["interval"]))

    @staticmethod
    def get_zones():
        return set(r["zone_id"] for r in ConfigHelper.get_rules())

    @staticmethod
    def get_max_ping_cnt():
        return int(ConfigHelper.__CONFIG["max_ping_cnt"])

    @staticmethod
    def get_away_temperature():
        return int(ConfigHelper.__CONFIG["away_temperature"])

    @staticmethod
    def get_client_state_history_len():
        return int(ConfigHelper.__CONFIG["client_state_history_len"])

    @staticmethod
    def get_min_home_success_pings():
        return int(ConfigHelper.__CONFIG["min_home_success_pings"])

    @staticmethod
    def get_print_timestamp():
        return ConfigHelper.__CONFIG["print_timestamp"]

    @staticmethod
    def get_allow_deep_sleep():
        return bool(ConfigHelper.__CONFIG["allow_deep_sleep"])

    @staticmethod
    def get_allow_deep_sleep():
        return bool(ConfigHelper.__CONFIG["allow_deep_sleep"])

    @staticmethod
    def get_deep_sleep_after_seconds():
        return float(ConfigHelper.__CONFIG["deep_sleep_after_hours"]) * 60 * 60

    @staticmethod
    def get_deep_sleep_temperature():
        return int(ConfigHelper.__CONFIG["deep_sleep_temperature"])

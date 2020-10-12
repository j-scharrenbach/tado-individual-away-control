"""
    File name: App.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 10/12/2020
    Python Version: 3.8
"""

from src.TadoWrapper import TadoWrapper
from src.ConfigHelper import ConfigHelper
from src.LoggingHelper import LoggingHelper
from src.ClientState import ClientState as cs
from src.ZoneState import ZoneState as zs

import ping3

import sys
import time


class App:
    def __init__(self):
        ConfigHelper.initialize()
        self.__tado = TadoWrapper()
        self.__zone_states = None

        self.__client_states = None
        self.__client_state_history = list()

    def list_zones(self):
        # print all zones of the home
        print("Zones in home:")
        for z in self.__tado.get_zones():
            print(z["id"], ":\t", z["name"])

    def __ping(self, ip):
        result = False
        for i in range(0, ConfigHelper.get_max_ping_cnt()):
            try:
                result = ping3.ping(ip, timeout=3) is not None
            except OSError:
                pass
            if result:
                break
        return result

    def __get_client_states(self):
        # returns the client states (available via ping or not)
        # checks if consecutive pings fail and set to away after defined number of pings
        new_c_states = {ip: cs.UNKNOWN for ip in ConfigHelper.get_ips()}

        for ip in new_c_states.keys():
            r = self.__ping(ip)

            if r:
                new_c_states[ip] = cs.HOME
            else:
                new_c_states[ip] = cs.AWAY

        if self.__client_states is None:
            self.__client_states = new_c_states

        # add to history and clean up
        self.__client_state_history.append(new_c_states)
        if len(self.__client_state_history) > ConfigHelper.get_client_state_history_len():
            self.__client_state_history.pop(0)

        # calculate presence for each ip
        for ip in new_c_states.keys():
            home_cnt = sum([h[ip] == cs.HOME for h in self.__client_state_history])

            if home_cnt >= ConfigHelper.get_min_home_success_pings():
                # home
                self.__client_states[ip] = cs.HOME
            else:
                # away and steady
                self.__client_states[ip] = cs.AWAY

        return self.__client_states

    def __get_desired_zone_states(self, client_states):
        # returns the desired states of all zones defined in the config.json
        z_states = {zone_id: zs.OFF for zone_id in ConfigHelper.get_zones()}

        clients_home = set(c[0] for c in client_states.items() if c[1] == cs.HOME)

        for r in ConfigHelper.get_rules():
            if len(set(r["ips"]).intersection(clients_home)) != 0:
                z_states[r["zone_id"]] = zs.ON

        return z_states

    def __update_heating(self):
        client_states = self.__get_client_states()

        # parse rules an get desired states
        desired_zone_states = self.__get_desired_zone_states(client_states)

        if self.__zone_states is None:
            # invert for first run to initially turn everything to the desired state
            self.__zone_states = {z[0]: zs.invert(z[1]) for z in desired_zone_states.items()}

        # get zones to turn on
        turn_on = set(z[0] for z in desired_zone_states.items() if z[1] == zs.ON).intersection(
            set(z[0] for z in self.__zone_states.items() if z[1] == zs.OFF))

        # get zones to turn off
        turn_off = set(z[0] for z in desired_zone_states.items() if z[1] == zs.OFF).intersection(
            set(z[0] for z in self.__zone_states.items() if z[1] == zs.ON))

        for zone in turn_on:
            LoggingHelper.log("Switching zone {} to state 'on'... ".format(zone))
            self.__tado.reset_zone(zone)

        for zone in turn_off:
            LoggingHelper.log("Switching zone {} to state 'off'... ".format(zone))
            self.__tado.set_zone(zone, ConfigHelper.get_away_temperature())

        self.__zone_states = desired_zone_states

    def run(self):
        while 1:
            # loop forever
            t_start = time.time()

            self.__update_heating()

            duration = time.time() - t_start
            time.sleep(max(ConfigHelper.get_interval() - duration, 0))


if __name__ == "__main__":
    app = App()
    if len(sys.argv) == 2 and sys.argv[1] == "--list-zones":
        app.list_zones()
    else:
        LoggingHelper.log("Application running.")
        app.run()

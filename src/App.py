"""
    File name: App.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 27/10/2021
    Python Version: 3.8
"""

from src.TadoWrapper import TadoWrapper
from src.ConfigHelper import ConfigHelper
from src.LoggingHelper import LoggingHelper
from src.ClientState import ClientState as cs
from src.ZoneState import ZoneState as zs

import time


class App:
    def __init__(self):
        ConfigHelper.initialize()
        self.__tado = TadoWrapper()
        self.__zone_states = None
        self.__zone_off_time = dict()
        self.__last_states = {}
        self.__geofencing_locked = None

        ConfigHelper.initialize_zones(self.__tado.get_zones())

    def list_devices(self):
        # print all devices connected to the home
        print("Devices in home:")
        for z in self.__tado.get_devices():
            print("\"" + z["name"] + "\"", end="")
            if not z["geo_tracking"]:
                print(" (no geo tracking enabled!)")
            else:
                print("")

    def list_zones(self):
        # print all zones of the home
        print("Zones in home:")
        for z in self.__tado.get_zones():
            print(z["id"], ":\t", z["name"])

    def __get_client_states(self):
        # returns the client states (at home or not)
        device_states = self.__tado.get_device_athome_states()
        client_states = {}

        # calculate presence for each device
        for d in ConfigHelper.get_devices():
            if d in device_states:
                state = device_states[d]
                if state["stale"]:
                    # set to default_stale_state if device is stale
                    default_state = ConfigHelper.get_default_stale_state()
                    if default_state == "SUSTAIN":
                        if d in self.__last_states:
                            client_states[d] = self.__last_states[d]
                        else:
                            client_states[d] = cs.HOME
                    elif default_state == "AWAY":
                        client_states[d] = cs.AWAY
                    else:
                        client_states[d] = cs.HOME
                else:
                    client_states[d] = cs.HOME if state["at_home"] else cs.AWAY
            else:
                raise Exception("Unknown device {}".format(d))

        self.__last_states = client_states

        return client_states

    def __get_desired_zone_states(self, client_states):
        # returns the desired states of all zones defined in the config.json
        z_states = {zone_id: zs.OFF for zone_id in ConfigHelper.get_zones()}

        clients_home = set(c[0] for c in client_states.items() if c[1] == cs.HOME)

        for r in ConfigHelper.get_rules():
            if len(set(r["device"]).intersection(clients_home)) != 0:
                z_states[r["zone_id"]] = zs.ON
                if r["zone_id"] in self.__zone_off_time.keys():
                    # remove from off time if turned on
                    self.__zone_off_time.pop(r["zone_id"])
            elif ConfigHelper.get_allow_deep_sleep():
                if r["zone_id"] in self.__zone_off_time.keys():
                    if (time.time() - self.__zone_off_time[r["zone_id"]]) > ConfigHelper.get_deep_sleep_after_seconds():
                        # set to deep sleep
                        z_states[r["zone_id"]] = zs.DEEP_SLEEP
                else:
                    # save time when state was set to off
                    self.__zone_off_time[r["zone_id"]] = time.time()

        return z_states

    def __update_heating(self):
        client_states = self.__get_client_states()
        geofencing_locked = self.__tado.is_presence_locked()

        # parse rules an get desired states
        desired_zone_states = self.__get_desired_zone_states(client_states)

        if not geofencing_locked:
            # geofencing not locked, contiue regular operation
            if self.__geofencing_locked:
                LoggingHelper.log("Geofencing unlocked, continue regular operation...")

            if self.__zone_states is None:
                # invert for first run to initially turn everything to the desired state
                self.__zone_states = {z[0]: zs.invert(z[1]) for z in desired_zone_states.items()}

            # get zones to turn on
            turn_on = set(z[0] for z in desired_zone_states.items() if z[1] == zs.ON).intersection(
                set(z[0] for z in self.__zone_states.items() if z[1] != zs.ON))

            # get zones to turn off
            turn_off = set(z[0] for z in desired_zone_states.items() if z[1] == zs.OFF).intersection(
                set(z[0] for z in self.__zone_states.items() if z[1] != zs.OFF))

            # get zones to turn to deep sleep mode
            turn_deep_sleep = set(z[0] for z in desired_zone_states.items() if z[1] == zs.DEEP_SLEEP).intersection(
                set(z[0] for z in self.__zone_states.items() if z[1] != zs.DEEP_SLEEP))

            for zone in turn_on:
                LoggingHelper.log("Switching zone {} to state 'on'... ".format(zone))
                self.__tado.reset_zone(zone)

            for zone in turn_off:
                LoggingHelper.log("Switching zone {} to state 'off'... ".format(zone))
                self.__tado.set_zone(zone, ConfigHelper.get_away_temperature())

            for zone in turn_deep_sleep:
                LoggingHelper.log("Switching zone {} to state 'deep sleep'... ".format(zone))
                self.__tado.set_zone(zone, ConfigHelper.get_deep_sleep_temperature())

            self.__zone_states = desired_zone_states

        elif not self.__geofencing_locked and geofencing_locked:
            # reset all zones which are set to off
            if self.__zone_states:
                off_zone_ids = [z[0] for z in self.__zone_states.items() if z[1] == zs.OFF]
                
                LoggingHelper.log("Geofencing locked, resetting all zones which are turned off...")
                for zone_id in off_zone_ids:
                    self.__tado.reset_zone(zone_id)
            
            LoggingHelper.log("Pausing until geofencing is unlocked.")

        self.__geofencing_locked = geofencing_locked

    def run(self):
        while 1:
            # loop forever
            t_start = time.time()

            self.__update_heating()

            duration = time.time() - t_start
            time.sleep(max(ConfigHelper.get_interval() - duration, 0))

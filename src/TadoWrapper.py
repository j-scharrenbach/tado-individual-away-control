"""
    File name: TadoWrapper.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 06/10/2021
    Python Version: 3.8
"""

from PyTado.interface import Tado

from src.ConfigHelper import ConfigHelper as c
from src.LoggingHelper import LoggingHelper

import time
from requests import exceptions as r_exc

class TadoWrapperException(Exception):
    pass

class TadoWrapper:
    CONNECTION_RETRY_INTERVAL = 60

    def __init__(self):
        self.__t = None
        self.__reconnect()

    def __connect(self):
        username, password = c.get_credentials()
        self.__t = Tado(username, password)

    def __reconnect(self):
        connected = False
        while not connected:
            LoggingHelper.log("Trying to connect to Tado... ")

            try:
                self.__connect()
                connected = True
                LoggingHelper.log("Connection to Tado established.")
            except r_exc.RequestException as e:
                LoggingHelper.log("Connection to Tado failed. Trying again in {} seconds.".format(TadoWrapper.CONNECTION_RETRY_INTERVAL))
                LoggingHelper.log(e)
                time.sleep(TadoWrapper.CONNECTION_RETRY_INTERVAL)

    def get_zones(self):
        data = self.__t.getZones()
        return [{"id": d["id"], "name": d["name"]} for d in data]

    def get_devices(self):
        data = self.__t.getMobileDevices()
        return [{"name": d["name"], "id": d["id"], "geo_tracking": d["settings"]["geoTrackingEnabled"]} for d in data]

    def set_zone(self, zone, temperature):
        success = False
        while not success:
            try:
                self.__t.setZoneOverlay(zone=zone, overlayMode="MANUAL", setTemp=temperature)
                success = True
                LoggingHelper.log("Zone {} set to {} degrees.".format(zone, temperature))
            except r_exc.RequestException as e:
                LoggingHelper.log("Unable to get device states.")
                LoggingHelper.log(e)
                self.__reconnect()

    def reset_zone(self, zone):
        success = False
        while not success:
            try:
                self.__t.resetZoneOverlay(zone=zone)
                success = True
                LoggingHelper.log("Zone {} reset to tado schedule.".format(zone))
            except r_exc.RequestException as e:
                LoggingHelper.log("Unable to get device states.")
                LoggingHelper.log(e)
                self.__reconnect()

    def get_device_athome_states(self):
        success = False
        data = None
        while not success:
            try:
                data = self.__t.getMobileDevices()
                if data is None:
                    raise TadoWrapperException("Mobile device data is None. Are any devices configured within Tado?")
                success = True
            except (r_exc.RequestException, TadoWrapperException) as e:
                LoggingHelper.log("Unable to get device states.")
                LoggingHelper.log(e)
                self.__reconnect()

        return {d["name"]: {"at_home": d["location"]["atHome"], "stale": d["location"]["stale"]} for d in data if d is not None and  "location" in d}

    def is_presence_locked(self):
        success = False
        data = None
        result = False
        while not success:
            try:
                data = self.__t.getHomeState()
                if data == None:
                    raise TadoWrapperException("Mobile device data is None. Are any devices configured within Tado?")
                success = True
            except (r_exc.RequestException, TadoWrapperException) as e:
                LoggingHelper.log("Unable to get device states.")
                LoggingHelper.log(e)
                self.__reconnect()
        if "presenceLocked" in data:
            result = data["presenceLocked"]
        return result

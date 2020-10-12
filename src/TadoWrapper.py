"""
    File name: TadoWrapper.py
    Author: Jannik Scharrenbach
    Date created: 10/10/2020
    Date last modified: 10/12/2020
    Python Version: 3.8
"""

from PyTado.interface import Tado

from src.ConfigHelper import ConfigHelper as c
from src.LoggingHelper import LoggingHelper

import time
from requests import exceptions as r_exc


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
            except (ConnectionError, r_exc.ReadTimeout, r_exc.ConnectionError, r_exc.ConnectTimeout):
                LoggingHelper.log("Connection to Tado failed. Trying again in {} seconds.".format(TadoWrapper.CONNECTION_RETRY_INTERVAL))
                time.sleep(TadoWrapper.CONNECTION_RETRY_INTERVAL)

    def get_zones(self):
        data = self.__t.getZones()
        return [{"id": d["id"], "name": d["name"]} for d in data]

    def set_zone(self, zone, temperature):
        success = False
        while not success:
            try:
                self.__t.setZoneOverlay(zone=zone, overlayMode="MANUAL", setTemp=temperature)
                success = True
                LoggingHelper.log("Zone {} turned off.".format(zone))
            except (ConnectionError, r_exc.ReadTimeout):
                LoggingHelper.log("Unable to set zone value.")
                self.__reconnect()

    def reset_zone(self, zone):
        success = False
        while not success:
            try:
                self.__t.resetZoneOverlay(zone=zone)
                success = True
                LoggingHelper.log("Zone {} turned on.".format(zone))
            except (ConnectionError, r_exc.ReadTimeout):
                LoggingHelper.log("Unable to reset zone.")
                self.__reconnect()

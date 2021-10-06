"""
    File name: App.py
    Author: Jannik Scharrenbach
    Date created: 10/12/2020
    Date last modified: 10/12/2020
    Python Version: 3.8
"""

from src.App import App
from src.LoggingHelper import LoggingHelper

import sys

if __name__ == "__main__":
    app = App()
    if len(sys.argv) == 2 and sys.argv[1] == "--list-zones":
        app.list_zones()
    elif len(sys.argv) == 2 and sys.argv[1] == "--list-devices":
        app.list_devices()
    else:
        LoggingHelper.log("Application running.")
        app.run()

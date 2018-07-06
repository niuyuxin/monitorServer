#!/usr/bin/env python3

from PyQt5.QtCore import *

class Config(QObject):
    MonitorName = "MonitorName"
    MonitorHoldDevice = "MonitorHoldDevice"
    MonitorSocket = "Socket"
    MonitorId = "MonitorId"
    def __init__(self, parent = None):
        super().__init__(parent)

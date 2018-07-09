#!/usr/bin/env python3

import  sys
from PyQt5.QtCore import *


def getFunctionName():
    return sys._getframe().f_back.f_code.co_name

class Config(QObject):
    MonitorName = "MonitorName"
    MonitorHoldDevice = "MonitorHoldDevice"
    MonitorSocket = "Socket"
    MonitorId = "MonitorId"
    def __init__(self, parent = None):
        super().__init__(parent)

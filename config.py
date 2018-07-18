#!/usr/bin/env python3

import  sys
from PyQt5.QtCore import *
import base64

def getFunctionName():
    return sys._getframe().f_back.f_code.co_name

class Config(QObject):
    MonitorName = "MonitorName"
    MonitorHoldDevice = "MonitorHoldDevice"
    MonitorSocket = "Socket"
    MonitorId = "MonitorId"
    SettingsName = "touchScreenServer.ini"
    def __init__(self, parent = None):
        super().__init__(parent)
        set = QSettings(Config.SettingsName, QSettings.IniFormat)
        set.setIniCodec(QTextCodec.codecForName("UTF-8"))
        if set.value("Version") != "180719.6":
            set.clear()
            set.setValue("Ip", "world")
            self.cryptoSetValue("Password", "123", set)
            set.beginGroup("Account")
            set.setValue("User1", "root")
            set.endGroup()
            set.beginGroup("Password")
            self.cryptoSetValue("root", "123456", set)
            set.endGroup()
            set.sync()
    @staticmethod
    def value(key):
        set = QSettings(Config.SettingsName, QSettings.IniFormat)
        set.setIniCodec(QTextCodec.codecForName("UTF-8"))
        return set.value(key)
    @staticmethod
    def setValue(key, value):
        set = QSettings(Config.SettingsName, QSettings.IniFormat)
        set.setIniCodec(QTextCodec.codecForName("UTF-8"))
        return set.setValue(key, value)
    @staticmethod
    def cryptoValue(key, set=None):
        if not set:
            set = QSettings(Config.SettingsName, QSettings.IniFormat)
        set.setIniCodec(QTextCodec.codecForName("UTF-8"))
        v = set.value(key)
        return str(base64.decodestring(bytes(v, encoding="utf-8")), encoding="utf-8")
    @staticmethod
    def cryptoSetValue(key, value, set=None):
        if not set:
            set = QSettings(Config.SettingsName, QSettings.IniFormat)
        set.setIniCodec(QTextCodec.codecForName("UTF-8"))
        value = str(base64.encodestring(bytes(value, encoding="utf-8")), encoding="utf-8")
        return set.setValue(key, value)
    @staticmethod
    def getGroupKeys(group):
        set = QSettings(Config.SettingsName, QSettings.IniFormat)
        set.beginGroup(group)
        keys = set.allKeys()
        set.endGroup()
        return keys
#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QHostAddress

class DataBaseException(Exception):pass
class DataBase(QObject):
    dataBaseName = "TouchScreen.db"
    dataBaseVersion = "180712"
    DeviceInfoTable = "DeviceInfo"
    PlayInfoTable = "PlayInfo"
    SceneInfoTable = "SceneInfo"
    DeviceSetInfoTable = "DeviceSetInfo"
    def __init__(self, parent = None):
        super().__init__(parent)
        self.dataBase = QSqlDatabase.addDatabase("QSQLITE")
        self.dataBase.setDatabaseName(DataBase.dataBaseName)
        self.dataBase.setUserName("root")
        self.dataBase.setPassword("123456")
        if not self.dataBase.open():
            print("{} opened failed, reaseon:".format(DataBase.dataBaseName),
                  self.dataBase.lastError().text())
            pass # Fixme: should show some message to user.
        sqlQuery = QSqlQuery(self.dataBase)
        update = True
        tables = self.dataBase.tables()
        if "VersionInfo" in tables:
            if sqlQuery.exec_("SELECT version FROM {}".format("VersionInfo")):
                if sqlQuery.next():
                    ver = sqlQuery.value(0)
                    if ver == DataBase.dataBaseVersion:
                        update = False
                        print("database version:", ver)
        if update:
            for t in tables:
                if t != "sqlite_sequence":
                    sqlQuery.exec_("DROP TABLE {table}".format(table=t))
        self.createDatabaseTable()
    def createDatabaseTable(self):
        sqlQuery = QSqlQuery(self.dataBase)
        sqlQuery.exec_("""CREATE TABLE VersionInfo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                    version VARCHAR(20) NOT NULL,
                    description VARCHAR(40) NOT NULL)""")
        sqlQuery.exec_("INSERT INTO VersionInfo (version, description) "
                    "VALUES ({ver}, 'Initialization version')".format(ver=DataBase.dataBaseVersion))
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS DeviceInfo (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                name VARCHAR NOT NULL,
                                devGroup VARCHAR NOT NULL,
                                devIndex INTEGER NOT NULL,
                                currentPos INTEGER,
                                upLimitedPos INTEGER,
                                downLimitedPos INTEGER,
                                zeroPos INTEGER,
                                mutexDev INTEGER)""")
        print(ret)
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS {tableName} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                name VARCHAR NOT NULL,
                                sceneIndex VARCHAR
                                )""".format(tableName=DataBase.PlayInfoTable))
        print(ret)
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS {tableName} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                name VARCHAR NOT NULL,
                                index VARCHAR NOT NULL,
                                deviceSetIndex VARCHAR
                                )""".format(tableName=DataBase.SceneInfoTable))
        print(ret)
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS {tableName} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                index VARCHAR NOT NULL,
                                deviceIndex VARCHAR
                                )""".format(tableName=DataBase.DeviceSetInfoTable))
        print(ret)
    def addPlays(self, table = "", item = dict()):
        print("insertRecord", item)
    def rmPlays(self, table = "", item = dict()):
        print("select Record", item)
    def searchPlays(self):
        pass
    def changePlays(self):
        pass
    def addScene(self):
        pass
    def rmScene(self):
        pass
    def searchScene(self):
        pass
    def changePlays(self):
        pass
    def addDeviceSet(self):pass
    def rmDeviceSet(self):pass
    def searchDeviceSet(self):pass
    def changeDeviceSet(self):pass

    # @pyqtSlot(str, list)
    def createDevicesInfo(self, monitorName, devices):
        # i = 0
        # while True:
        #     print("database", i)
        #     i += 1
        print(monitorName, devices)
        sqlQuery = QSqlQuery(self.dataBase)
        ret = self.rmDeviceInfo(item="devGroup", value=monitorName, sqlQuery=sqlQuery)
        if not ret:
            return
        count = 0
        for dev in devices:
            insertStr = """INSERT INTO {tableName} (name, devIndex, devGroup) VALUES ('{name}', {index}, '{group}')"""\
                        .format(tableName=DataBase.DeviceInfoTable, name=dev, index=count, group=monitorName)
            print(insertStr)
            print(sqlQuery.exec_(insertStr))
            count += 1
    def rmDeviceInfo(self, item, value, sqlQuery=None):
        if not sqlQuery:
            sqlQuery = QSqlQuery(self.dataBase)
        if isinstance(value, list):
            for v in value:
                ret = sqlQuery.exec_("""DELETE FROM {table} WHERE {item} = {v}"""
                               .format(table=DataBase.DeviceInfoTable, item=item, v=v))
        else:
            ret = sqlQuery.exec_("""DELETE FROM {table} WHERE {item} = '{v}'"""
                           .format(table=DataBase.DeviceInfoTable, item=item, v=value))
        return ret
    def searchDeviceInfo(self):pass
    def changeDeviceInfo(self):pass


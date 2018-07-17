#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtSql import QSqlQuery, QSqlDatabase, QSqlRecord
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QHostAddress

class DataBaseException(Exception):pass
class DataBase(QObject):
    dataBaseName = "TouchScreen.db"
    dataBaseVersion = "180715.9"
    DeviceInfoTable = "DeviceInfo"
    PlayInfoTable = "PlayInfo"
    SceneInfoTable = "SceneInfo"
    DeviceSetInfoTable = "DeviceSetInfo"
    databaseState = pyqtSignal(bool)
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
        sqlQuery = QSqlQuery("PRAGMA synchronous = OFF;", self.dataBase)
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
                                devName VARCHAR NOT NULL,
                                devGroup VARCHAR NOT NULL,
                                selfIndex VARCHAR NOT NULL,
                                currentPos INTEGER,
                                upLimitedPos INTEGER,
                                downLimitedPos INTEGER,
                                zeroPos INTEGER,
                                targetPos INTEGER,
                                devSpeed INTEGER,
                                mutexDev INTEGER)""")
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS {tableName} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                selfIndex VARCHAR NOT NULL,
                                playName VARCHAR NOT NULL,
                                editingTime TEXT
                                )""".format(tableName=DataBase.PlayInfoTable))
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS {tableName} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                sceneName VARCHAR NOT NULL,
                                selfIndex VARCHAR NOT NULL,
                                parentIndex VARCHAR
                                )""".format(tableName=DataBase.SceneInfoTable))
        ret = sqlQuery.exec_("""CREATE TABLE IF NOT EXISTS {tableName} (
                                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                                selfIndex VARCHAR NOT NULL,
                                parentIndex VARCHAR NOT NULL,
                                deviceIndex VARCHAR NOT NULL,
                                targetPos INT,
                                devSpeed INT
                                )""".format(tableName=DataBase.DeviceSetInfoTable))
    def insertPlays(self, name, id):
        sqlQuery = QSqlQuery(self.dataBase)
        if sqlQuery.exec_("""SELECT selfIndex FROM PlayInfo"""):
            while sqlQuery.next():
                if sqlQuery.value(0) == id:
                    ret = sqlQuery.exec_("UPDATE PlayInfo SET playName='{n}' where selfIndex='{index}'"
                                   .format(n=name, index=id))
                    print("update Plays success", name, id)
                    return
            else:
                insertStr = "INSERT INTO PlayInfo (playName, selfIndex) VALUES ('{name}', '{id}')".format(name=name,id=id)
                if sqlQuery.exec_(insertStr):
                    print("insert Plays success", name, id)


    def rmPlays(self, table = "", item = dict()):
        print("select Record", item)
    def searchPlays(self):
        plays = {}
        sqlQuery = QSqlQuery("""SELECT * FROM PlayInfo""")
        rec = sqlQuery.record()
        nameCol = rec.indexOf("playName")
        indexCol = rec.indexOf("selfIndex")
        while sqlQuery.next():
            plays[sqlQuery.value(indexCol)] = sqlQuery.value(nameCol)
        return plays
    def changePlays(self, name, id):
        sqlQuery = QSqlQuery(self.dataBase)
        if sqlQuery.exec_("UPDATE PlayInfo SET playName={nn} where selfIndex='{id}'".format(nn=newName, id=id)):
            print("insert success")
    def insertScene(self, name, id):
        sqlQuery = QSqlQuery(self.dataBase)
        if sqlQuery.exec_("""SELECT selfIndex FROM SceneInfo"""):
            while sqlQuery.next():
                if sqlQuery.value(0) == id:
                    ret = sqlQuery.exec_("UPDATE SceneInfo SET sceneName='{n}' where selfIndex='{index}'"
                                   .format(n=name, index=id))
                    print("update scene success", name, id)
                    return
            else:
                insertStr = "INSERT INTO SceneInfo (SceneName, selfIndex) VALUES ('{name}', '{id}')".format(name=name,id=id)
                if sqlQuery.exec_(insertStr):
                    print("insert scene success", name, id)
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
    def getAllDevicesInfo(self, subDevDict):
        sqlQuery = QSqlQuery("SELECT * FROM DeviceInfo", self.dataBase)
        rec = sqlQuery.record()
        nameCol = rec.indexOf("devName")
        groupCol = rec.indexOf("devGroup")
        while sqlQuery.next():
            devGroup = sqlQuery.value(groupCol)
            if devGroup not in subDevDict.keys():
                subDevDict[devGroup] = [sqlQuery.value(nameCol)]
            else:
                subDevDict[devGroup].append(sqlQuery.value(nameCol))

    @pyqtSlot(str, list)
    def onCreateDevicesInfo(self, monitorName, devices):
        self.databaseState.emit(True)
        sqlQuery = QSqlQuery(self.dataBase)
        ret = self.rmDeviceInfo(item="devGroup", value=monitorName, sqlQuery=sqlQuery)
        count = 0
        for dev in devices:
            insertStr = """INSERT INTO DeviceInfo (devName, selfIndex, devGroup, targetPos, devSpeed) 
                            VALUES ('{name}', '{index}', '{group}', {targetPos}, {devSpeed})"""\
                        .format(name=dev, index=dev + ':' + str(count), group=monitorName, targetPos=1000, devSpeed=50)
            if not sqlQuery.exec_(insertStr):
                print("[sqlQuery exec error]", insertStr)
            count += 1
        print(self.tr("创建设备完成")+"{cur}/{all}" .format(cur=count, all=len(devices)))
        self.databaseState.emit(False)
    def rmDeviceInfo(self, item, value, sqlQuery=None):
        if not sqlQuery:
            sqlQuery = QSqlQuery(self.dataBase)
        if isinstance(value, list):
            for v in value:
                ret = sqlQuery.exec_("""DELETE FROM {table} WHERE {item} = '{v}'"""\
                               .format(table=DataBase.DeviceInfoTable, item=item, v=v))
        else:
            ret = sqlQuery.exec_("""DELETE FROM {table} WHERE {item} = '{v}'"""\
                           .format(table=DataBase.DeviceInfoTable, item=item, v=value))
        return ret
    def searchDeviceInfo(self):pass
    def changeDeviceInfo(self):pass

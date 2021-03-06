#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtSql import QSqlQuery, QSqlDatabase, QSqlRecord
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtNetwork import QHostAddress
from devattr import *
class DataBaseException(Exception):pass
class DataBase(QObject):
    dataBaseName = "TouchScreen.db"
    dataBaseVersion = "180715.15"
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
                                devUserState INT2,
                                devPlcState INT4,
                                selfIndex VARCHAR NOT NULL,
                                plcId VARCHAR NOT NULL,
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

    def openDatabaseForName(self, dataBase, connectionName):
        dataBase = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        dataBase.setDatabaseName(DataBase.dataBaseName)
        dataBase.setUserName("root")
        dataBase.setPassword("123456")
        if not dataBase.open():
            print("{} opened failure".format(connectionName))

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
    def getAllDevices(self, subDevDict, detailInfoList):
        sqlQuery = QSqlQuery(self.dataBase)
        # setDevice = {} Todo:更新编场信息的位置和速度
        # if sqlQuery.exec_("""SELECT selfIndex, deviceIndex, targetPos, devSpeed FROM DeviceSetInfo"""):
        #     setDevice[sqlQuery.value(0)] = [sqlQuery.value(1), sqlQuery.value(2), sqlQuery.value(3)]
        if sqlQuery.exec_("SELECT * FROM DeviceInfo"):
            rec = sqlQuery.record()
            nameCol = rec.indexOf("devName")
            groupCol = rec.indexOf("devGroup")
            plcCol = rec.indexOf("plcId")
            upperLimitCol = rec.indexOf("upLimitedPos")
            lowerLimitCol = rec.indexOf("downLimitedPos")
            targetPosCol = rec.indexOf("targetPos")
            devSpeedCol = rec.indexOf("devSpeed")
            while sqlQuery.next():
                devGroup = sqlQuery.value(groupCol)
                plcId = sqlQuery.value(plcCol)
                name = sqlQuery.value(nameCol)
                upperLimit = sqlQuery.value(upperLimitCol)
                lowerLimit = sqlQuery.value(lowerLimitCol)
                targetPos = sqlQuery.value(targetPosCol)
                devSpeed = sqlQuery.value(devSpeedCol)
                if devGroup not in subDevDict.keys():
                    subDevDict[devGroup] = [[plcId, name]]
                else:
                    subDevDict[devGroup].append([plcId, name])
                dev = DevAttr(plcId, name)
                dev.targetPos = targetPos if targetPos else 0
                dev.upLimitedPos = upperLimit if upperLimit else 0
                dev.downLimitedPos = lowerLimit if lowerLimit else 0
                dev.devSpeed = devSpeed
                # if name in setDevice.keys():
                #     dev.programId = setDevice[name][0]
                #     dev.programSetPos = setDevice[name][1]
                #     dev.programSetSpeed = setDevice[name][2]
                detailInfoList.append(dev)
    @pyqtSlot(str, list)
    def onCreateDevicesInfo(self, monitorName, devices):
        self.databaseState.emit(True)
        sqlQuery = QSqlQuery(self.dataBase)
        ret = self.rmDeviceInfo(item="devGroup", value=monitorName, sqlQuery=sqlQuery)
        count = 0
        for dev in devices:
            insertStr = """INSERT INTO DeviceInfo (devName, selfIndex, devGroup, plcId, targetPos, devSpeed) 
                            VALUES ('{name}', '{index}', '{group}', '{plcId}', {targetPos}, {devSpeed})"""\
                        .format(name=dev[1],
                                index=dev[1] + ':' + str(count),
                                group=monitorName,
                                plcId = dev[0],
                                targetPos=0,
                                devSpeed=50)
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
    def onSavingParaSetting(self, devName, targetPos, upperLimit, lowerLimit):
        sqlQuery = QSqlQuery(self.dataBase)
        if sqlQuery.exec_("""UPDATE DeviceInfo 
                            SET upLimitedPos={},downLimitedPos={},targetPos={} 
                            WHERE devName='{}'""".format(upperLimit, lowerLimit, targetPos, devName)):
            pass
        else:
            print("...error")

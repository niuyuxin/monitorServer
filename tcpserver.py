#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from config import  *
from PyQt5.QtSql import *
from database import  *
import ast
import json
import random

class TcpServer(QObject):
    Modal = "Modal"
    getAllSubDev = pyqtSignal(str, list)
    updateDeviceState = pyqtSignal(int, list)
    updateParaSetting = pyqtSignal(int, dict)
    Call = 2
    CallResult = 3
    CallError = 4
    InfoScreen = "infoScreen"
    TouchScreen = "TouchScreen"
    ParaSetting = "ParaSetting"
    DeviceStateChanged = "DeviceStateChanged"
    ForbiddenDevice = "ForbiddenDevice"
    SetScreen = "setScreen"
    SetScreenValue = "value"
    MonitorName = "MonitorName"
    MonitorDevice = "MonitorDevice"
    MonitorSocket = "Socket"
    MonitorId = "MonitorId"
    MonitorRecBuf = "RecBuf"
    MonitorDeviceCount = "MonitorDeviceCount"
    UpdateDevice = "UpdateDevice"
    def __init__(self):
        super().__init__()
        self.dataBase =  self.openDatabaseForName("TcpServerConnection")
        self.tcpServer = QTcpServer(self) # should have parent
        self.sendCount = 0
        self.socketList = []
        if not self.tcpServer.listen(QHostAddress.AnyIPv4, 5000):
            print("listen error")
            return
        else:
            self.tcpServer.newConnection.connect(self.onNewConnection)
            print("listen successful")
    @pyqtSlot()
    def onNewConnection(self):
        while self.tcpServer.hasPendingConnections():
            socket = self.tcpServer.nextPendingConnection()
            socket.readyRead.connect(self.onReadyToRead)
            socket.disconnected.connect(self.onSocketDisconnect)
            socketDict = {TcpServer.MonitorSocket:socket,
                          TcpServer.MonitorId:None,
                          TcpServer.MonitorDevice:[],
                          TcpServer.MonitorName:None,
                          TcpServer.MonitorDeviceCount:0}
            self.socketList.append(socketDict)
            print("socket accpet ", socketDict)
            b = QByteArray(bytes(r"Hello, New tcpSocket... [socket IpV4 = {}]".format(socket.peerAddress().toString()), encoding="UTF-8"))
            socket.write(b)

    @pyqtSlot()
    def onSocketDisconnect(self):
        socket = self.sender()
        count = 0
        for s in self.socketList:
            if s[TcpServer.MonitorSocket] == socket:
                self.updateDeviceState.emit(s[TcpServer.MonitorId], [])
                self.socketList.pop(count)
                print("Delete socket: ", socket)
            count += 1
        socket.deleteLater()

    @pyqtSlot()
    def onReadyToRead(self):
        try:
            socket = self.sender()
            socketDict = {}
            for s in self.socketList:
                if s[TcpServer.MonitorSocket] == socket:
                    socketDict = s
                    break
            if not socketDict:
                print("socket {} is not in socketList".format(socketDict))
                return
            while socket.bytesAvailable():
                allData = str(socket.readAll(), encoding='UTF-8')
                dataList = allData.split('\0')
                print("Received: ", len(dataList[0]), dataList)
                for data in dataList:
                    if len(data) == 0: continue
                    dataJson = json.loads(data)
                    if len(dataJson) == 4 and dataJson[0] == TcpServer.Call:
                        if socketDict[TcpServer.MonitorName] == None or socketDict[TcpServer.MonitorId] == None:
                            dataDict = dataJson[3]
                            if isinstance(dataDict, dict):
                                socketDict[TcpServer.MonitorId] = int(dataDict.get(TcpServer.MonitorId))
                                socketDict[TcpServer.MonitorDeviceCount] = dataDict.get(TcpServer.MonitorDeviceCount)
                                socketDict[TcpServer.MonitorName] = dataDict.get(TcpServer.MonitorName)
                                message = [TcpServer.CallResult, dataJson[1], dataJson[2], {}]
                                socket.write(bytes(json.dumps(message, ensure_ascii='UTF-8'), encoding='utf-8')+b'\0')
                                socket.waitForBytesWritten()
                            else:
                                socket.disconnectFromHost()
                        elif len(socketDict[TcpServer.MonitorDevice]) != socketDict[TcpServer.MonitorDeviceCount]:
                            if dataJson[2] == TcpServer.UpdateDevice:
                                if isinstance(dataJson[3], dict) and isinstance(dataJson[3][TcpServer.MonitorDevice], list):
                                    socketDict[TcpServer.MonitorDevice].extend(dataJson[3][TcpServer.MonitorDevice])
                                if len(socketDict[TcpServer.MonitorDevice]) == socketDict[TcpServer.MonitorDeviceCount]:
                                    self.updateDeviceState.emit(socketDict[TcpServer.MonitorId], [])
                                    self.getAllSubDev.emit(socketDict[TcpServer.MonitorName], socketDict[TcpServer.MonitorDevice])
                                devInfo = []
                                for dev in dataJson[3][TcpServer.MonitorDevice]:
                                    data = [dev[1]]
                                    data.extend(self.getDevInfo(dev[1]))
                                    devInfo.append(data)
                                message = [TcpServer.CallResult, dataJson[1], dataJson[2], {"Device":devInfo}]
                                socket.write(bytes(json.dumps(message, ensure_ascii='UTF-8'), encoding='utf-8')+b'\0')
                                socket.waitForBytesWritten()
                        else:
                            self.analysisData(socketDict, dataJson)
        except Exception as e:
            tempDict = {"Error:{}".format(str(e)): data}
            b = QByteArray(bytes(str(tempDict), encoding="UTF-8")).append("\n")
            socket.write(b)

    def analysisData(self, socketDict, dataList):
        try:
            action = dataList[2]
            if action == TcpServer.DeviceStateChanged:
                id = int(socketDict[TcpServer.MonitorId])
                self.updateDeviceState.emit(id, dataList[3]["Device"])
            elif action == TcpServer.ParaSetting:
                self.updateParaSetting.emit(-1, dataList[3])
            else:
                print("Unknow request: {}".format(action))
        except Exception as e:
            print("analysis Data", str(e))

    def onDataToSend(self, name, id, messageList): # messageTypeId, action, data
        try:
            message = []
            if len(messageList) == 4:
                message = messageList
            else:
                message = [messageList[0], self.createUnionId(messageList[1]), messageList[1], messageList[2]]
            self.sendDataToSocket(name, id, bytes(json.dumps(message, ensure_ascii='UTF-8'), encoding='utf-8') + b'\0')
        except Exception as e:
            print("onDataToSend", str(e))

    def sendDataToSocket(self, name, id, data): # 选择要发给的设备
        sendSocket = None
        try:
            for socket in self.socketList:
                if socket[TcpServer.MonitorName] == name and \
                    socket[TcpServer.MonitorId] == id and \
                    socket[TcpServer.MonitorSocket].state() == QAbstractSocket.ConnectedState:
                    sendSocket = socket[TcpServer.MonitorSocket]
                    sendSocket.write(data)
                    sendSocket.waitForBytesWritten()
        except Exception as e:
            print("onsendData", str(e))

    def createUnionId(self, type):
        time = QDateTime.currentDateTime().toString("yyMMddhhmmsszzz")
        self.sendCount += 1
        return str(type) + '-' + time + '-' + str(self.sendCount)

    def openDatabaseForName(self, connectionName):
        dataBase = QSqlDatabase.addDatabase("QSQLITE", connectionName)
        dataBase.setDatabaseName(DataBase.dataBaseName)
        dataBase.setUserName("root")
        dataBase.setPassword("123456")
        if not dataBase.open():
            print("{} opened failure".format(connectionName))
            return None
        else:
            QSqlQuery("PRAGMA synchronous = OFF;", dataBase)
            return dataBase
    def getDevInfo(self, devName):
        for dev in GlobalVal.devInfoList:
            if dev.devName == devName:
                return [dev.targetPos, dev.upLimitedPos, dev.downLimitedPos, dev.ctrlWord]
        return []
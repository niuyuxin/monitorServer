#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from config import  *

class TcpServer(QObject):
    getAllSubDev = pyqtSignal(str, list)
    def __init__(self):
        super().__init__()
        self.tcpServer = QTcpServer()
        self.socketList = []
        if not self.tcpServer.listen(QHostAddress.AnyIPv4, 5000):
            print("listen error")
            return
        else:
            self.tcpServer.newConnection.connect(self.onNewConnection)
            print("listen successful")
    @pyqtSlot()
    def onNewConnection(self):
        while True:pass
        if self.tcpServer.hasPendingConnections():
            socket = self.tcpServer.nextPendingConnection()
            socket.readyRead.connect(self.onReadyToRead)
            socket.disconnected.connect(self.onSocketDisconnect)
            socketDict = {Config.MonitorSocket:socket,
                          Config.MonitorId:None,
                          Config.MonitorHoldDevice:None,
                          Config.MonitorName:None}
            self.socketList.append(socketDict)
            print("socket accpet ", socket)
            b = QByteArray(bytes(r"Hello, New tcpSocket... \n socket IpV4 = {}".format(socket.peerAddress().toString()), encoding="UTF-8"))
            socket.write(b)
    def onSocketDisconnect(self):
        socket = self.sender()
        count = 0
        for s in self.socketList:
            if s[Config.MonitorSocket] == socket:
                self.socketList.pop(count)
                print("delete socket name", socket)
            count += 1
        socket.deleteLater()
    def onReadyToRead(self):
        for socketDict in self.socketList:
            if socketDict[Config.MonitorSocket].isValid and socketDict[Config.MonitorSocket].bytesAvailable():
                data = socketDict[Config.MonitorSocket].readAll()
                if len(data) > 1472:
                    print("[waring] Getting data of size is: ", len(data))
                if socketDict[Config.MonitorId] is None:
                    dataDict = self.checkData(data)
                    if isinstance(dataDict, dict) and Config.MonitorId in dataDict.keys():
                        socketDict[Config.MonitorId] = dataDict.get(Config.MonitorId)
                        socketDict[Config.MonitorHoldDevice] = dataDict.get(Config.MonitorHoldDevice)
                        socketDict[Config.MonitorName] = dataDict.get(Config.MonitorName)
                        self.analysisData(dataDict)
                        socketDict[Config.MonitorSocket].write(data)
                    else:
                        socketDict[Config.MonitorSocket].disconnectFromHost()
                else:
                    socketDict[Config.MonitorSocket].write(data)

    def checkData(self, data):
        di = eval(str(data, encoding='utf-8'))
        if isinstance(di, dict):
            return di
        else:
            pass
    def analysisData(self, dataDict):
            allDevice = dataDict.get(Config.MonitorHoldDevice)
            monitorName = dataDict.get(Config.MonitorName)
            if allDevice and monitorName:
                self.getAllSubDev.emit(monitorName, allDevice)


#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from config import  *
import ast

class TcpServer(QObject):
    Modal = "Modal"
    getAllSubDev = pyqtSignal(str, list)
    selectedDevice = pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.tcpServer = QTcpServer(self) # should have parent
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
            socketDict = {Config.MonitorSocket:socket,
                          Config.MonitorId:None,
                          Config.MonitorHoldDevice:None,
                          Config.MonitorName:None}
            self.socketList.append(socketDict)
            print("socket accpet ", socketDict)
            b = QByteArray(bytes(r"Hello, New tcpSocket... [socket IpV4 = {}]".format(socket.peerAddress().toString()), encoding="UTF-8"))
            socket.write(b)
    @pyqtSlot()
    def onSocketDisconnect(self):
        socket = self.sender()
        count = 0
        for s in self.socketList:
            if s[Config.MonitorSocket] == socket:
                self.socketList.pop(count)
                print("delete socket name", socket)
            count += 1
        socket.deleteLater()
    @pyqtSlot()
    def onReadyToRead(self):
        socket = self.sender()
        socketDict = {}
        for s in self.socketList:
            if s[Config.MonitorSocket] == socket:
                socketDict = s
                break
        if not socketDict:
            print("socket {} is not in socketList".format(socketDict))
            return
        while socket.bytesAvailable():
            data = socket.readAll()
            print("[waring] Getting data of size is: ", len(data))
            try:
                dataDict = ast.literal_eval(str(data, encoding="UTF-8"))
                if not socketDict[Config.MonitorName] or not socketDict[Config.MonitorId]:
                    if isinstance(dataDict, dict):
                        socketDict[Config.MonitorId] = dataDict.get(Config.MonitorId)
                        socketDict[Config.MonitorHoldDevice] = dataDict.get(Config.MonitorHoldDevice)
                        socketDict[Config.MonitorName] = dataDict.get(Config.MonitorName)
                        allDevice = dataDict.get(Config.MonitorHoldDevice)
                        monitorName = dataDict.get(Config.MonitorName)
                        if allDevice and monitorName:
                            self.getAllSubDev.emit(monitorName, allDevice)
                        print(socketDict)
                        # socket.write(data)
                    else:
                        socket.disconnectFromHost()
                else:
                    self.analysisData(dataDict)
                    # socket.write(data)
            except Exception as e:
                print("error:", str(e))
                tempDict = {"Error":"Hello"}
                b = QByteArray(bytes(str(tempDict), encoding="UTF-8"))
                socket.write(b)

    def analysisData(self, dataDict):
        for item in dataDict.items():
            if item[0].upper() == "selectedDevice".upper():
                print("selectedDevice", item[1])
                self.selectedDevice.emit(item[1])

    def onSendData(self, name, data):
        sendSocket = None
        try:
            for socket in self.socketList:
                if socket[Config.MonitorName] == name and \
                        socket[Config.MonitorSocket].state() == QAbstractSocket.ConnectedState:
                    sendSocket = socket[Config.MonitorSocket]
                    break
        except Exception as e:
            print(str(e))
        if sendSocket:
            tempDict = {TcpServer.Modal: 1}
            b = QByteArray(bytes(str(tempDict), encoding="UTF-8"))
            sendSocket.write(b)

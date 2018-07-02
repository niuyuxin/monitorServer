#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *


class TcpServer(QObject):
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
    def onNewConnection(self):
        if self.tcpServer.hasPendingConnections():
            socket = self.tcpServer.nextPendingConnection()
            socket.readyRead.connect(self.onReadyToRead)
            socket.disconnected.connect(self.onSocketDisconnect)
            self.socketList.append(socket)
            socket.write(QByteArray(bytes("Hello, New tcpSocket...", encoding="UTF-8")))
    def onSocketDisconnect(self):
        socket = self.sender()
        socket.deleteLater()
        self.socketList.remove(socket)
    def onReadyToRead(self):
        for socket in self.socketList:
            if socket.isValid and socket.bytesAvailable():
                d = socket.readAll()
                print(str(d, encoding='utf-8'))
                socket.write(d)

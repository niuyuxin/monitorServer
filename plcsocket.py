#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from config import *
import collections
import ast
import json

class PlcSocket(QObject):
    tcpState=pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
    @pyqtSlot()
    def initTcpSocket(self):
        self.testCount = 0
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connected.connect(self.onTcpSocketConnected)
        self.tcpSocket.readyRead.connect(self.onTcpSocketReadyRead)
        self.tcpSocket.disconnected.connect(self.onTcpSocketDisconnected)
        self.tcpSocket.error.connect(self.onTcpSocketError)
        self.connectTimer = QTimer(self)
        self.connectTimer.timeout.connect(self.connectServer, Qt.DirectConnection)
        self.connectTimer.start(1000)

    @pyqtSlot()
    def onTcpSocketConnected(self):
        print("Tcp socket connected!")
        self.tcpState.emit(self.tcpSocket.state())
        self.connectTimer.stop()

    def sendData(self, data):
        if self.tcpSocket.state() == QAbstractSocket.ConnectedState:
            self.tcpSocket.write(data)
            self.tcpSocket.waitForBytesWritten()
        else:
            print("网络不可用")

    @pyqtSlot()
    def connectServer(self):
        if self.tcpSocket.state() == QAbstractSocket.UnconnectedState:
            ip = Config.value("PlcIp")
            socketIp = ip if ip else QHostAddress(QHostAddress.LocalHost)
            port = int(Config.value("PlcPort"))
            socketPort = port if port else 2000
            print("Connect to server: ", socketIp, socketPort)
            self.tcpSocket.connectToHost(QHostAddress(socketIp), socketPort)
        elif self.tcpSocket.state() == QAbstractSocket.ConnectingState:
            self.tcpState.emit(self.tcpSocket.state())
            # print("Connecting...", QDateTime.currentDateTime().toString("hh:mm:ss.zzz"))

    @pyqtSlot()
    def onTcpSocketReadyRead(self):
        try:
            temp = self.tcpSocket.readAll()
            time = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
            print("Read data, size = {}:{}".format(len(temp), temp.toHex()), time)
            self.testCount += 1
            fillZero = []
            for i in range(6):
                fillZero.append(0)
            fillZero.insert(0, self.testCount>>8)
            fillZero.insert(1, self.testCount&0xff)
            temp = bytes(fillZero)
            print(QByteArray(temp))
            self.tcpSocket.write(QByteArray(temp))
            self.tcpSocket.waitForBytesWritten()
        except Exception as e:
            print("onTcpSocketReadyRead", str(e))

    @pyqtSlot()
    def onTcpSocketDisconnected(self):
        print("Tcp socket disconnected")
        self.connectTimer.start(1000)

    @pyqtSlot(QAbstractSocket.SocketError)
    def onTcpSocketError(self, err):
        print("Tcp Socket error", err)
        self.tcpSocket.disconnectFromHost()
        self.connectTimer.start(1000)

    @pyqtSlot(int)
    def onTcpSocketManagement(self, code):
        if code:
            self.tcpSocket.abort()
            print("on tcp socket abort()")


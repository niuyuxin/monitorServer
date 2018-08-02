#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from config import *
import collections
from globalvariable import GlobalVal

class PlcSocket(QObject):
    tcpState=pyqtSignal(int)
    MaxBufferSize = 2000
    def __init__(self, parent=None):
        super().__init__(parent)
    @pyqtSlot()
    def initTcpSocket(self):
        self.testCount = 0
        self.tcpSocket = QTcpSocket(self)
        self.tcpSocketBuffer = []
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
            if len(self.tcpSocketBuffer) < PlcSocket.MaxBufferSize:
                b = temp.data()
                self.tcpSocketBuffer.extend(b)
            else:
                self.tcpSocketBuffer = []
                self.tcpSocketBuffer.extend(temp.data())

            if len(self.tcpSocketBuffer) != PlcSocket.MaxBufferSize:
                return
            time = QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
            # print("Read data, size = {}:{}".
            #       format(len(self.tcpSocketBuffer), self.tcpSocketBuffer), time)
            self.callReturn()
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

    def callReturn(self):
        count = 0
        devInfoList = []
        for devList in GlobalVal.monitorSubDevDict.values():
            devInfoList.extend(devList)
        sendBuffer = QByteArray()
        for dev in devInfoList:
            infoList = self.getDevInfoForName(dev[1])
            devid = int(dev[0][8:])&0xff
            order = 0
            infoList.insert(0, order)
            infoList.insert(0, devid)
            sendBuffer.append(bytes(infoList))

        print(sendBuffer.toHex())
        # self.testCount += 1
        # fillZero = []
        # for i in range(self.testCount, 20 + self.testCount):
        #     fillZero.append(i & 0xff)
        # temp = bytes(fillZero)
        # print('send', QByteArray(temp).toHex())
        # self.tcpSocket.write(QByteArray(temp))
        # self.tcpSocket.waitForBytesWritten()

    def getDevCtrlWordForName(self, devName):
        byteInfo = 0
        for devInfo in GlobalVal.deviceStateList.values():
            if not devInfo: continue
            d = False
            for dev in devInfo:
                if dev[0] == devName:
                    d = True
                    if dev[1] == 1: # 选通
                        byteInfo |= (1<<13)
                    if dev[1] == 2: # 禁用
                        byteInfo |= (1<<5)
                    if dev[1] == 4: # 旁路
                        byteInfo |= (1<<14)
                    if GlobalVal.singleCtrlOperation == -1: # 下降
                        byteInfo |= (0x4<<8)
                    elif GlobalVal.singleCtrlOperation == 1: # 上升
                        byteInfo |= (0x1<<8)
                    else: # 停止
                        byteInfo |= (0x2<<8)
            if d:
                return byteInfo&0xffff
        return byteInfo&0xffff

    def getDevInfoForName(self, devName): # 返回 速度、目标位置、控制字、上软限、下软限
        speed = GlobalVal.singleCtrlSpeed
        targetPos = 0
        cWord = self.getDevCtrlWordForName(devName)
        upLimit = 9000 # 从数据库获取数据
        downLimit = 0
        return [(speed>>8)&0xff, speed&0xff,
                (targetPos>>24)&0xff, (targetPos>>16)&0xff, (targetPos>>8)&0xff, (targetPos)&0xff,
                (cWord>>8)&0xff, cWord&0xff,
                (upLimit >> 24) & 0xff, (upLimit >> 16) & 0xff, (upLimit >> 8) & 0xff, (upLimit) & 0xff,
                (downLimit >> 24) & 0xff, (downLimit >> 16) & 0xff, (downLimit >> 8) & 0xff, (downLimit) & 0xff]


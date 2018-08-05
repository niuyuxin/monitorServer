#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtNetwork import *
from PyQt5.QtCore import *
from config import *
import collections
from devattr import DevAttr

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
            print("Read data, size = {}:{}".
                  format(len(self.tcpSocketBuffer), self.tcpSocketBuffer), time)
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
        """
        对plc的发送做出响应
        :return:
        """
        try:
            sendBuffer = QByteArray()
            count = 0
            for devAttr in DevAttr.devAttrList:
                infoList = self.getDevInfo(devAttr)
                devid = int(devAttr.devId[8:])&0xff
                infoList.insert(0, 0) # order
                infoList.insert(0, devid) # devId
                while len(infoList) < 20:
                    infoList.append(0)
                sendBuffer.append(bytes(infoList))
                count += 1
                if count >= 100: break
            # data = sendBuffer
            # dataList = []
            # for i in range(0, data.size(), 20):
            #     dataList.append(bytes(data.mid(i, 20).toHex()))
            # print(dataList)
            self.tcpSocket.write(sendBuffer)
            self.tcpSocket.waitForBytesWritten()
        except Exception as e:
            print("call return ", str(e))

    def getDevInfo(self, dev):
        """
        :param dev: 要获取的设备
        :return: 返回 速度、目标位置、控制字、上软限、下软限
        """
        if dev.section in DevAttr.singleCtrlSpeed.keys():
            speed = DevAttr.singleCtrlSpeed[dev.section]
        else:
            speed = 0
        targetPos = dev.targetPos
        cWord = self.getDevCtrlWord(dev)
        upLimit = dev.upLimitedPos
        downLimit = dev.downLimitedPos
        return [(speed>>8)&0xff, speed&0xff,
                (targetPos>>24)&0xff, (targetPos>>16)&0xff, (targetPos>>8)&0xff, (targetPos)&0xff,
                (cWord>>8)&0xff, cWord&0xff,
                (upLimit >> 24) & 0xff, (upLimit >> 16) & 0xff, (upLimit >> 8) & 0xff, (upLimit) & 0xff,
                (downLimit >> 24) & 0xff, (downLimit >> 16) & 0xff, (downLimit >> 8) & 0xff, (downLimit) & 0xff]

    def getDevCtrlWord(self, dev):
        ctrlWord = dev.ctrlWord
        ctrlWord &= (~(DevAttr.CW_Raise | DevAttr.CW_Drop | DevAttr.CW_Stop))
        if dev.section in DevAttr.singleCtrlOperation.keys():
            if DevAttr.singleCtrlOperation[dev.section] == -1: # 下降
                ctrlWord |= DevAttr.CW_Drop
            elif DevAttr.singleCtrlOperation[dev.section] == 1: # 上升
                ctrlWord |= DevAttr.CW_Raise
            else: # 停止
                ctrlWord |= DevAttr.CW_Stop
        else:
            ctrlWord |= DevAttr.CW_Stop

        return ctrlWord&0xffff



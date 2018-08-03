#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import ui_mainwindow
from tcpserver import TcpServer
from devicedatawidget import  DevDataWidget
from deviceprogramwidget import DevProgramWidget
from devicegraphicwidget import  DeviceGraphicWidget
from organizedplay import OrganizedPlay
from database import DataBase
from systemmanagement import *
from devicenetgraphic import *
from plcsocket import *
from globalvariable import *
import collections

class MainWindow(QWidget, ui_mainwindow.Ui_Form):
    plcSocketManagement = pyqtSignal(int)
    getMonitorDevice = pyqtSignal(str, list)
    getPlaysInfo = pyqtSignal()
    sendDataToTcp = pyqtSignal(str, int, list) # name, id, messageTypeId, action, data
    savingParaSetting = pyqtSignal(str, int, int, int)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.initMainWindow()
    def initMainWindow(self):
        # create Device Data Widget
        self.devDataWidget = None
        self.devGraphicWidget = None
        self.devProgramWidget  = None
        self.contentWidgetList = []
        # real time object
        self.rtc = QTimer()
        self.rtc.timeout.connect(self.onRtcTimeout)
        self.onRtcTimeout()
        self.rtc.start(1000)
        # create mysql database
        self.dataBase = DataBase()
        self.dataBase.getAllDevices(GlobalVal.monitorSubDevDict, GlobalVal.devInfoList)
        self.dataBase.databaseState.connect(self.onDatabaseState)
        self.dataBaseThread = QThread()
        self.dataBase.moveToThread(self.dataBaseThread)
        self.getMonitorDevice.connect(self.dataBase.onCreateDevicesInfo)
        self.savingParaSetting.connect(self.dataBase.onSavingParaSetting)
        self.dataBaseThread.start()
        # frame
        self.contentFrameLayout = QHBoxLayout()
        self.contentFrame.setLayout(self.contentFrameLayout)
        # self.contentFrameLayout.setContentsMargins(0,0,0,0)
        # graphic view
        self.devGraphicWidget = DeviceGraphicWidget(self.getAllDevice())  # new widget
        self.devGraphicWidget.sendDataToTcp.connect(self.sendDataToTcp)
        self.contentFrameLayout.addWidget(self.devGraphicWidget)
        self.contentWidgetList.append(self.devGraphicWidget)
        # program running..
        self.devProgramWidget = DevProgramWidget()
        self.contentFrameLayout.addWidget(self.devProgramWidget)
        self.contentWidgetList.append(self.devProgramWidget)
        self.devProgramWidget.sendDataToTcp.connect(self.sendDataToTcp)
        self.showAllDeviceInWidget()
        # create tcp server, main function...
        self.tcpServer = TcpServer()
        self.tcpServerThread = QThread()
        self.tcpServer.moveToThread(self.tcpServerThread)
        self.tcpServer.getAllSubDev.connect(self.onTcpServerGetAllSubDev)
        self.tcpServer.updateDeviceState.connect(self.devGraphicWidget.onUpdateDeviceState)
        self.tcpServer.updateParaSetting.connect(self.onTcpServerUpdateSetting)
        self.sendDataToTcp.connect(self.tcpServer.onDataToSend)
        self.tcpServerThread.start()
        # plc Socket
        self.plcSocket = PlcSocket()
        self.plcSocketThread = QThread()
        self.plcSocket.moveToThread(self.plcSocketThread)
        self.plcSocketManagement.connect(self.plcSocket.onTcpSocketManagement)
        self.plcSocketThread.started.connect(self.plcSocket.initTcpSocket)
        self.plcSocketThread.start()

        # push button signal and slots
        self.dataShowingPushButton.clicked.connect(self.onDataShowingPushButtonClicked)
        self.graphicShowingPushButton.clicked.connect(self.onGraphicShowingPushButtonClicked)
        self.autoRunningPushButton.clicked.connect(self.onAutoRunningPushButtonClicked)
        self.organizedPlayPushButton.clicked.connect(self.onOrganizedPlayPushButtonClicked)
        self.systemManagementPushButton.clicked.connect(self.onSystemManagementPushButtonClicked)
        self.netFramePushButton.clicked.connect(self.onNetFramePushButtonClicked)

    def onRtcTimeout(self):
        self.timeLabel.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))

    @pyqtSlot(str, list)
    def onTcpServerGetAllSubDev(self, monitorName, subDev):
        if GlobalVal.monitorSubDevDict.get(monitorName) == subDev:
            print("Got same monitor device!", monitorName, subDev)
            return
        if GlobalVal.monitorSubDevDict.get(monitorName) is None:
            GlobalVal.monitorSubDevDict.setdefault(monitorName, subDev)
        else:
            GlobalVal.monitorSubDevDict[monitorName] = subDev
        self.getMonitorDevice.emit(monitorName, subDev)
        print("some thing changed...", subDev)
        GlobalVal.devInfoList = self.createDevInfoDict() # 需要等待数据库创建完成以后再生成此变量
        self.showAllDeviceInWidget()

    def getAllDevice(self):
        allDevice = []
        for key in GlobalVal.monitorSubDevDict.keys():
            for dev in GlobalVal.monitorSubDevDict[key]:
                allDevice.append(dev[1])
        return allDevice

    def createDevInfoDict(self):
        devInfo = []
        for key in GlobalVal.monitorSubDevDict.keys():
            for dev in GlobalVal.monitorSubDevDict[key]:
                devInfo.append(DevAttr(dev[0], dev[1]))
        return devInfo

    def showAllDeviceInWidget(self):
        if self.devDataWidget is not None:
            self.contentWidgetList.remove(self.devDataWidget)
            self.contentFrameLayout.removeWidget(self.devDataWidget)
            self.devDataWidget.deleteLater()
        self.devDataWidget = DevDataWidget(GlobalVal.devInfoList)  # new widget
        self.devDataWidget.sendDataToTcp.connect(self.sendDataToTcp)
        self.contentFrameLayout.addWidget(self.devDataWidget)
        self.contentWidgetList.append(self.devDataWidget)
        self.showWidgetInContentWidget(widget=self.devDataWidget)

    def onDataShowingPushButtonClicked(self):
        if self.devDataWidget is not None:
            self.showWidgetInContentWidget(widget=self.devDataWidget)
    def onGraphicShowingPushButtonClicked(self):
        self.showWidgetInContentWidget(widget=self.devGraphicWidget)

    def onAutoRunningPushButtonClicked(self):
        self.showWidgetInContentWidget(widget=self.devProgramWidget)

    def onOrganizedPlayPushButtonClicked(self):
        try:
            organizedPlay = OrganizedPlay()
            organizedPlay.playsActive.connect(self.devProgramWidget.onAutoRunning)
            print("organizedPlay exit code:", organizedPlay.exec_())
        except Exception as e:
            print("create organized play error", str(e))
    def showWidgetInContentWidget(self, index = 0, widget = None):
        for w in self.contentWidgetList:
            w.hide()
        if widget is None:
            if len(self.contentWidgetList) != 0:
                self.contentWidgetList[0].show()
        else:
            widget.show()

    def onDatabaseState(self, s):
        if s:
            self.databaseLabel.setText("数据库忙")
        else:
            self.databaseLabel.setText("数据库闲")
    def onSystemManagementPushButtonClicked(self):
        login = AccountLogin()
        if login.exec_():
            try:
                sysManagement = SystemManagement()
                sysManagement.somthingChanged.connect(self.onSysManagementSomthingChanged)
                sysManagement.exec_()
            except Exception as e:
                print(str(e))
    def onNetFramePushButtonClicked(self):
        try:
            deviceNetGraphic = DeviceNetGraphic(self.getAllDevice())
            for dev in self.getAllDevice():
                deviceNetGraphic.stateChanged(dev, False, True)
            deviceNetGraphic.exec_()
        except Exception as e:
            print(str(e))

    @pyqtSlot(str, str)
    def onSysManagementSomthingChanged(self, name, value):
        self.plcSocketManagement.emit(1)

    @pyqtSlot(int, dict)
    def onTcpServerUpdateSetting(self, sec, setting):
        try:
            id = setting["DevId"]
            targetPos =  setting["targetPos"]
            UpLimited = setting["UpLimited"]
            DownLimited = setting["DownLimited"]
            for dev in GlobalVal.devInfoList:
                if dev.devId == id:
                    dev.targetPos = targetPos
                    dev.upLimitedPos = UpLimited
                    dev.downLimitedPos = DownLimited
                    if dev.targetPos > 100:
                        dev.setStateWord(DevAttr.SW_LowerLimit)
                    else:
                        dev.clearStateWord(DevAttr.SW_LowerLimit)
                    dev.valueChanged.emit(dev.devId, dev.devName)
                    self.savingParaSetting.emit(dev.devName, targetPos, UpLimited, DownLimited)
        except Exception as e:
            print("On Tcp Server update Setting", str(e))

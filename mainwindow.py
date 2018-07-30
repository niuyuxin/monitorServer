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
import collections

class MainWindow(QWidget, ui_mainwindow.Ui_Form):
    getMonitorDevice = pyqtSignal(str, list)
    getPlaysInfo = pyqtSignal()
    sendDataToTcp = pyqtSignal(str, int, list) # name, id, messageTypeId, action, data
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.initMainWindow()
    def initMainWindow(self):
        # real time object
        self.rtc = QTimer()
        self.rtc.timeout.connect(self.onRtcTimeout)
        self.onRtcTimeout()
        self.rtc.start(1000)

        # create mysql database
        self.monitorSubDevDict = {}
        self.dataBase = DataBase()
        self.dataBase.getAllDevicesInfo(self.monitorSubDevDict)
        self.dataBase.databaseState.connect(self.onDatabaseState)
        self.dataBaseThread = QThread()
        self.dataBase.moveToThread(self.dataBaseThread)
        self.getMonitorDevice.connect(self.dataBase.onCreateDevicesInfo)
        self.dataBaseThread.start()

        # create Device Data Widget
        self.devDataWidget = None
        self.devGraphicWidget = None
        self.devProgramWidget  = None
        self.contentWidgetList = []

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
        self.tcpServer.updateDeviceState.connect(self.devGraphicWidget.onSelectedDevice)
        self.sendDataToTcp.connect(self.tcpServer.onDataToSend)
        self.tcpServerThread.start()

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
        if self.monitorSubDevDict.get(monitorName) == subDev:
            print("Got same monitor device!")
            return
        if self.monitorSubDevDict.get(monitorName) is None:
            self.monitorSubDevDict.setdefault(monitorName, subDev)
        else:
            self.monitorSubDevDict[monitorName] = subDev
        self.getMonitorDevice.emit(monitorName, subDev)
        print("some thing changed...", subDev)
        self.showAllDeviceInWidget()
    def getAllDevice(self):
        allDevice = []
        for key in self.monitorSubDevDict.keys():
            for dev in self.monitorSubDevDict[key]:
                allDevice.append(dev[1])
        return allDevice
    def showAllDeviceInWidget(self):
        if self.devDataWidget is not None:
            self.contentWidgetList.remove(self.devDataWidget)
            self.contentFrameLayout.removeWidget(self.devDataWidget)
            self.devDataWidget.deleteLater()
        self.devDataWidget = DevDataWidget(self.getAllDevice())  # new widget
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
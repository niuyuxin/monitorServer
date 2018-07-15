#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import ui_mainwindow
from tcpserver import TcpServer
from devicedatawidget import  DevDataWidget
from deviceautorunningwidget import DeviceAutoRunningWidget
from devicegraphicwidget import  DeviceGraphicWidget
from organizedplay import OrganizedPlay
from database import DataBase

class MainWindow(QWidget, ui_mainwindow.Ui_Form):
    getMonitorDevice = pyqtSignal(str, list)
    getPlaysInfo = pyqtSignal()
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
        # create Device Data Widget
        self.devDataWidget = None
        self.devGraphicWidget = None
        self.devAutoRunningWidget  = None
        self.monitorSubDevDict = {}
        self.contentWidgetList = []

        # create mysql database
        self.dataBase = DataBase()
        self.dataBase.getAllDevicesInfo(self.monitorSubDevDict)
        self.dataBase.databaseState.connect(self.onDatabaseState)
        self.dataBaseThread = QThread()
        self.dataBase.moveToThread(self.dataBaseThread)
        self.getMonitorDevice.connect(self.dataBase.onCreateDevicesInfo)
        self.dataBaseThread.start()
        # create tcp server, main function...
        self.tcpServer = TcpServer()
        self.tcpServerThread = QThread()
        self.tcpServer.moveToThread(self.tcpServerThread)
        self.tcpServer.getAllSubDev.connect(self.onTcpServerGetAllSubDev)
        self.tcpServerThread.start()

        self.contentFrameLayout = QHBoxLayout()
        self.contentFrame.setLayout(self.contentFrameLayout)
        # self.contentFrameLayout.setContentsMargins(0,0,0,0)
        # Todo: get local device of monitor
        self.showAllDeviceInWidget()
        # push button signal and slots
        self.dataShowingPushButton.clicked.connect(self.onDataShowingPushButtonClicked)
        self.graphicShowingPushButton.clicked.connect(self.onGraphicShowingPushButtonClicked)
        self.autoRunningPushButton.clicked.connect(self.onAutoRunningPushButtonClicked)
        self.organizedPlayPushButton.clicked.connect(self.onOrganizedPlayPushButtonClicked)

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
        print("some thing changed...")
        self.showAllDeviceInWidget()
    def showAllDeviceInWidget(self):
        allDevice = []
        for key in self.monitorSubDevDict.keys():
            for dev in self.monitorSubDevDict[key]:
                allDevice.append(dev)
        if self.devDataWidget is not None:
            self.contentWidgetList.remove(self.devDataWidget)
            self.contentFrameLayout.removeWidget(self.devDataWidget)
            self.devDataWidget.deleteLater()
        if self.devGraphicWidget is not None:
            self.contentWidgetList.remove(self.devGraphicWidget)
            self.contentFrameLayout.removeWidget(self.devGraphicWidget)
            self.devGraphicWidget.deleteLater()
        self.devDataWidget = DevDataWidget(allDevice)  # new widget
        self.contentFrameLayout.addWidget(self.devDataWidget)
        self.contentWidgetList.append(self.devDataWidget)

        self.devGraphicWidget = DeviceGraphicWidget(allDevice)  # new widget
        self.contentFrameLayout.addWidget(self.devGraphicWidget)
        self.contentWidgetList.append(self.devGraphicWidget)
        self.showWidgetInContentWidget(widget=self.devDataWidget)

    def onDataShowingPushButtonClicked(self):
        if self.devDataWidget is not None:
            self.showWidgetInContentWidget(widget=self.devDataWidget)
    def onGraphicShowingPushButtonClicked(self):
        self.showWidgetInContentWidget(widget=self.devGraphicWidget)
    def onAutoRunningPushButtonClicked(self):
        self.showWidgetInContentWidget(widget=self.devAutoRunningWidget)
    def onOrganizedPlayPushButtonClicked(self):
        plays = self.dataBase.searchPlays()
        try:
            organizedPlay = OrganizedPlay(plays=plays, subDevDict=self.monitorSubDevDict)
            organizedPlay.insertPlays.connect(self.dataBase.insertPlays)
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

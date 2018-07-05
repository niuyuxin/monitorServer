#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui import ui_mainwindow
from tcpserver import TcpServer
from devicedatawidget import  DevDataWidget
from deviceautorunningwidget import DeviceAutoRunningWidget
from devicegraphicwidget import  DeviceGraphicWidget


class MainWindow(QWidget, ui_mainwindow.Ui_Form):
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
        # create tcp server, main function...
        self.tcpServer = TcpServer()
        self.tcpServer.getAllSubDev.connect(self.onTcpServerGetAllSubDev)
        self.contentFrameLayout = QHBoxLayout()
        self.contentFrame.setLayout(self.contentFrameLayout)
        # self.contentFrameLayout.setContentsMargins(0,0,0,0)
        # create Device Data Widget
        self.devDataWidget = None
        self.devGraphicWidget = None
        self.devAutoRunningWidget  = None
        self.contentWidgetList = []
        # push button signal and slots
        self.dataShowingPushButton.clicked.connect(self.onDataShowingPushButtonClicked)
        self.graphicShowingPushButton.clicked.connect(self.onGraphicShowingPushButtonClicked)
        self.autoRunningPushButton.clicked.connect(self.onAutoRunningPushButtonClicked)
    def onRtcTimeout(self):
        self.timeLabel.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
    def onTcpServerGetAllSubDev(self, subDev):
        if self.devDataWidget is None:
            self.devDataWidget = DevDataWidget(subDev) # new widget
            self.contentFrameLayout.addWidget(self.devDataWidget)
            self.contentWidgetList.append(self.devDataWidget)
            self.devGraphicWidget = DeviceGraphicWidget(subDev) # new widget
            self.contentFrameLayout.addWidget(self.devGraphicWidget)
            self.contentWidgetList.append(self.devGraphicWidget)
            self.devAutoRunningWidget = DeviceAutoRunningWidget() # new widget
            self.contentFrameLayout.addWidget(self.devAutoRunningWidget)
            self.contentWidgetList.append(self.devAutoRunningWidget)
            self.showWidgetInContentWidget()
    def onDataShowingPushButtonClicked(self):
        if self.devDataWidget is not None:
            self.showWidgetInContentWidget(widget=self.devDataWidget)
            pass
    def onGraphicShowingPushButtonClicked(self):
        self.showWidgetInContentWidget(widget=self.devGraphicWidget)
    def onAutoRunningPushButtonClicked(self):
        self.showWidgetInContentWidget(widget=self.devAutoRunningWidget)
    def showWidgetInContentWidget(self, index = 0, widget = None):
        for w in self.contentWidgetList:
            w.hide()
        if widget is None:
            if len(self.contentWidgetList) != 0:
                self.contentWidgetList[0].show()
        else:
            widget.show()
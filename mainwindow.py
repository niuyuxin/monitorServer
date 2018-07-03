#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ui import ui_mainwindow
from tcpserver import TcpServer
from devicedatawidget import  DevDataWidget

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
        self.contentFrameLayout = QVBoxLayout()
        self.contentFrame.setLayout(self.contentFrameLayout)
        # create Device Data Widget
        self.devDataWidget = None
    def onRtcTimeout(self):
        self.timeLabel.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
    def onTcpServerGetAllSubDev(self, subDev):
        if self.devDataWidget is None:
            self.devDataWidget = DevDataWidget(subDev)
            self.contentFrameLayout.addWidget(self.devDataWidget)
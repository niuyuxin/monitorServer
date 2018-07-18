#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlQuery, QSqlRecord, QSqlDatabase
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from database import DataBase
from ui import ui_deviceinfo
import  collections

class DeviceInfo(QFrame, ui_deviceinfo.Ui_DeviceInfo):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.devNameLabel.setText(name)

    def paintEvent(self, QPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
class DeviceAutoRunningWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.dataBase = QSqlDatabase.addDatabase("QSQLITE", "DeviceAutoRunningWidgetConnection")
        self.dataBase.setDatabaseName(DataBase.dataBaseName)
        self.dataBase.setUserName("root")
        self.dataBase.setPassword("123456")
        self.scenes = None
        if not self.dataBase.open():
            print("OrganizedPlay database opened failure")
        self.playNameLabel = QLabel("剧目名称")
        self.playNameLabel.setAlignment(Qt.AlignHCenter)
        self.sceneNameLabel = QLabel("场次名称")
        self.sceneNameLabel.setAlignment(Qt.AlignHCenter)
        self.prevPushButton = QPushButton("<<<")
        self.nextPushButton = QPushButton(">>>")
        self.sceneIndexCount = 0
        self.sceneIndexLabel = QLabel("1/1")
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.prevPushButton)
        self.buttonLayout.addWidget(self.sceneIndexLabel)
        self.buttonLayout.addWidget(self.nextPushButton)
        self.buttonLayout.setAlignment(Qt.AlignHCenter)
        self.prevPushButton.clicked.connect(self.onPrevPushButtonClicked)
        self.nextPushButton.clicked.connect(self.onNextPushButtonClicked)
        self.devScrollArea = QScrollArea()
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.playNameLabel)
        self.mainLayout.addWidget(self.sceneNameLabel)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addWidget(self.devScrollArea)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)
    def onAutoRunning(self, play, playName):
        self.playNameLabel.setText(playName)
        sqlQuery = QSqlQuery(self.dataBase)
        self.scenes = collections.OrderedDict()
        if sqlQuery.exec_("""SELECT selfIndex, sceneName FROM SceneInfo WHERE parentIndex='{}'""".format(play)):
            while sqlQuery.next():
                self.scenes[(sqlQuery.value(0), sqlQuery.value(1))] = []
        for key in self.scenes:
            if sqlQuery.exec_("""SELECT deviceIndex FROM DeviceSetInfo WHERE parentIndex='{}'""".format(key[0])):
                while sqlQuery.next():
                    self.scenes[key].append(sqlQuery.value(0))
        if self.scenes:
            self.showScenes(0)
    def showScenes(self, scenesNumber):
        index = 0
        for item in self.scenes.items():
            if index == scenesNumber:
                self.sceneNameLabel.setText(item[0][1]) # set scene title
                column = 0
                row = 0
                devGridLayout = QGridLayout()
                for dev in item[1]:
                    widget = DeviceInfo(name=dev)
                    devGridLayout.addWidget(widget, row, column)
                    column += 1
                    if column >= 8:
                        column = 0
                        row += 1
                break
            index += 1
        devWidget = QWidget()
        devWidget.setLayout(devGridLayout)
        self.devScrollArea.setWidget(devWidget)
        self.sceneIndexLabel.setText("{}/{}".format(scenesNumber + 1, len(self.scenes)))

    def onNextPushButtonClicked(self):
        if not self.scenes: return
        if self.sceneIndexCount >= (len(self.scenes)-1):
            self.sceneIndexCount = 0
        else:
            self.sceneIndexCount += 1
        self.showScenes(self.sceneIndexCount)

    def onPrevPushButtonClicked(self):
        if not self.scenes: return
        if self.sceneIndexCount > 0:
            self.sceneIndexCount -= 1
        else:
            self.sceneIndexCount = len(self.scenes)-1
        self.showScenes(self.sceneIndexCount)
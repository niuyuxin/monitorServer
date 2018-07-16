#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlQuery, QSqlRecord, QSqlDatabase
from PyQt5.QtCore import *
from database import DataBase
from ui import ui_deviceinfo
import  collections

class DeviceInfo(QWidget, ui_deviceinfo.Ui_DeviceInfo):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.devNameLabel.setText(name)
class DeviceAutoRunningWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.dataBase = QSqlDatabase.addDatabase("QSQLITE", "DeviceAutoRunningWidgetConnection")
        self.dataBase.setDatabaseName(DataBase.dataBaseName)
        self.dataBase.setUserName("root")
        self.dataBase.setPassword("123456")
        if not self.dataBase.open():
            print("OrganizedPlay database opened failure")
        self.playNameLabel = QLabel("剧目名称")
        self.playNameLabel.setAlignment(Qt.AlignHCenter)
        self.sceneNameLabel = QLabel("场次名称")
        self.sceneNameLabel.setAlignment(Qt.AlignHCenter)
        self.prevPushButton = QPushButton("<<<")
        self.nextPushButton = QPushButton(">>>")
        self.sceneIndexCount = 0
        self.sceneIndexLabel = QLabel("1/2")
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
    def onAutoRunning(self, plays):
        sqlQuery = QSqlQuery(self.dataBase)
        self.scenes = collections.OrderedDict()
        if sqlQuery.exec_("""SELECT selfIndex, sceneName FROM SceneInfo WHERE parentIndex='{}'""".format(plays)):
            while sqlQuery.next():
                self.scenes[(sqlQuery.value(0), sqlQuery.value(1))] = []
        for key in self.scenes:
            if sqlQuery.exec_("""SELECT deviceIndex FROM DeviceSetInfo WHERE parentIndex='{}'""".format(key[0])):
                while sqlQuery.next():
                    self.scenes[key].append(sqlQuery.value(0))
        self.showScenes(0)
    def showScenes(self, scenesNumber):
        count = 0
        index = 0
        try:
            devWidget = QWidget()
            devGridLayout = QGridLayout()
            for item in self.scenes.items():
                if index == scenesNumber:
                    self.sceneNameLabel.setText(item[0][1])
                    for dev in item[1]:
                        widget = DeviceInfo(name=dev)
                        devGridLayout.addWidget(widget, 0, count)
                        count += 1
                    break
                index += 1
            devWidget.setLayout(devGridLayout)
            self.devScrollArea.setWidget(devWidget)
        except Exception as e:
            print(str(e))
    def onNextPushButtonClicked(self):
        allScenes = len(self.scenes)
        if self.sceneIndexCount >= (allScenes-1):
            self.sceneIndexCount = 0
        else:
            self.sceneIndexCount += 1
        self.showScenes(self.sceneIndexCount)
        self.sceneIndexLabel.setText("{}/{}".format(self.sceneIndexCount+1, allScenes))


    def onPrevPushButtonClicked(self):
        allScenes = len(self.scenes)
        if self.sceneIndexCount > 0:
            self.sceneIndexCount -= 1
        else:
            self.sceneIndexCount = len(self.scenes)-1
        self.showScenes(self.sceneIndexCount)
        self.sceneIndexLabel.setText("{}/{}".format(self.sceneIndexCount+1, allScenes))
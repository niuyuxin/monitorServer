#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from miscutils import DeviceInfoWidget
import json


class SubDevDataWidget(QTableWidget):
    showDeviceInfo = pyqtSignal(str)  # Fixme: this type should be 'subDev' type, just for testing in here.

    def __init__(self, subDeviceList = [], column=[], parent=None):
        super().__init__(parent)
        self.subDeviceList = subDeviceList
        self.devInformationWidget = DeviceInfoWidget(self)
        self.showDeviceInfo.connect(self.devInformationWidget.onDeviceInformation)
        self.mouseInRow = -1
        self.mouseInColumn = 0
        self.setColumnCount(len(column))
        self.setRowCount(len(subDeviceList))
        self.horizontalHeader().setStyleSheet("QHeaderView::section{background:skyblue;}")
        self.setHorizontalHeaderLabels(column)
        self.setVerticalHeaderLabels(subDeviceList)
        try:  # try to create sub contents
            for i in range(len(subDeviceList)):
                upCheckBox = QCheckBox("上限")
                downCheckBox = QCheckBox("下限")
                widget = QWidget()
                widget.setDisabled(True)
                layout = QHBoxLayout()
                layout.addWidget(upCheckBox)
                layout.addWidget(downCheckBox)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignHCenter)
                widget.setLayout(layout)
                self.setCellWidget(i, 3, widget)
                for c in range(3):
                    tableWidgetItem = QTableWidgetItem()
                    tableWidgetItem.setText("None")
                    self.setItem(i, c, tableWidgetItem)
        except Exception as e:
            print(str(e))
        # attribute setting, read code...
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setMouseTracking(True)  # should turn on mouse tracking when user cell entered
        self.cellEntered.connect(self.onCellEntered)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # set user can not change it
        # tigger informatin display
        self.triggerInfoDisplayTimer = QTimer()
        self.triggerInfoDisplayTimer.timeout.connect(self.onTriggerInfoDisplayTimerTimeout)
    def onCellEntered(self, row, column):
        if row != self.mouseInRow:
            self.triggerInfoDisplayTimer.start(1000)
            self.showDeviceInfo.emit(self.subDeviceList[row])
            self.devInformationWidget.hide()
            self.mouseInRow = row

    def enterEvent(self, *args, **kwargs):
        pass  # print("enter")

    def leaveEvent(self, *args, **kwargs):
        if not self.devInformationWidget.frameGeometry().contains(QCursor.pos()):
            self.devInformationWidget.hide()
        self.triggerInfoDisplayTimer.stop()

    def onTriggerInfoDisplayTimerTimeout(self):
        self.triggerInfoDisplayTimer.stop()
        self.devInformationWidget.show()


class DevDataWidget(QWidget):
    sendDataToTcp = pyqtSignal(str, int, str) # 屏幕，区号， 内容
    def __init__(self, subDevList=[], parent=None):
        super().__init__(parent)
        self.subDevDataWidgetList = []
        row = []
        count = 0
        perSubWidgetDevNumber = len(subDevList) // 4
        if len(subDevList) % 4 != 0:
            perSubWidgetDevNumber += 1
        # print(len(subDevList), perSubWidgetDevNumber)
        for dev in subDevList:
            if count % perSubWidgetDevNumber == 0:
                if len(row) != 0:
                    self.subDevDataWidgetList.append(row)
                row = []
            row.append(dev)
            count += 1
        self.subDevDataWidgetList.append(row)
        self.scrollBar = QScrollBar()
        self.scrollBar.setRange(0, perSubWidgetDevNumber)
        columnName = [self.tr("实际位置"), self.tr("上软限"), self.tr("下软限"), self.tr("限位开关")]
        self.hLayout = QHBoxLayout()
        for subWidget in self.subDevDataWidgetList:
            s = SubDevDataWidget(subWidget, columnName)
            self.scrollBar.valueChanged.connect(s.verticalScrollBar().setValue)
            self.hLayout.addWidget(s)
        self.hLayout.addWidget(self.scrollBar)
        self.setLayout(self.hLayout)
        self.hLayout.setSpacing(0)
    def showEvent(self, QShowEvent):
        for i in range(2):
            info = [2, "1234567890", "setScreen", {}]
            self.sendDataToTcp.emit("infoScreen", i, json.dumps(info, ensure_ascii=False))
        pass

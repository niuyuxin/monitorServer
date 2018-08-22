#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from miscutils import DeviceInfoWidget
from tcpserver import *
import json
from devattr import *

class SubDevDataWidget(QTableWidget):
    showDeviceInfo = pyqtSignal(str)  # Fixme: this type should be 'subDev' type, just for testing in here.

    def __init__(self, subDeviceList = [], column=[], parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.subDeviceList = subDeviceList
        self.devInformationWidget = DeviceInfoWidget(self)
        self.showDeviceInfo.connect(self.devInformationWidget.onDeviceInformation)
        self.mouseInRow = -1
        self.mouseInColumn = 0
        self.setColumnCount(len(column))
        self.setRowCount(len(subDeviceList))
        # self.verticalHeader().setMinimumHeight(100)
        self.setHorizontalHeaderLabels(column)
        vHeaderLabels = []
        for dev in subDeviceList:
            vHeaderLabels.append(dev.devName)
        self.setVerticalHeaderLabels(vHeaderLabels)
        try:  # try to create sub contents
            font = QFont(self.font())
            font.setPointSize(13)
            for i in range(len(subDeviceList)):
                self.setRowHeight(i, 60)
                self.subDeviceList[i].valueChanged.connect(self.onDevAttrValueChanged)
                item = QTableWidgetItem() # 位置
                item.setFont(font)
                item.setForeground(Qt.white)
                item.setTextAlignment(Qt.AlignVCenter|Qt.AlignHCenter)
                item.setText(str(subDeviceList[i].currentPos))
                self.setItem(i, 0, item)
                item = QTableWidgetItem() # 上限
                item.setFont(font)
                item.setForeground(Qt.white)
                item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                item.setText(str(subDeviceList[i].upLimitedPos))
                self.setItem(i, 1, item)
                item = QTableWidgetItem() # 下限
                item.setFont(font)
                item.setForeground(Qt.white)
                item.setTextAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
                item.setText(str(subDeviceList[i].downLimitedPos))
                self.setItem(i, 2, item)
                upCheckBox = QCheckBox("上限")
                upCheckBox.setAttribute(Qt.WA_TransparentForMouseEvents)
                downCheckBox = QCheckBox("下限")
                downCheckBox.setAttribute(Qt.WA_TransparentForMouseEvents)
                widget = QWidget()
                layout = QVBoxLayout()
                layout.addWidget(upCheckBox)
                layout.addWidget(downCheckBox)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setAlignment(Qt.AlignHCenter)
                widget.setLayout(layout)
                self.setCellWidget(i, 3, widget)
        except Exception as e:
            print(str(e))
        # attribute setting, read code...
        self.setFrameShape(QFrame.NoFrame)
        self.setSelectionMode(QAbstractItemView.NoSelection)
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
            self.showDeviceInfo.emit(self.subDeviceList[row].devName)
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

    def onDevAttrValueChanged(self, id, name):
        try:
            dev = self.sender()
            if not isinstance(dev, DevAttr):
                return
            for rc in range(self.rowCount()):
                if self.verticalHeaderItem(rc).text() == name:
                    posItem = self.item(rc, 0)
                    upLimitItem = self.item(rc, 1)
                    downLimitItem = self.item(rc, 2)
                    upReached = self.cellWidget(rc, 3).layout().itemAt(0).widget()
                    downReached = self.cellWidget(rc, 3).layout().itemAt(1).widget()
                    posItem.setText(str(dev.currentPos))
                    upLimitItem.setText(str(dev.upLimitedPos))
                    downLimitItem.setText(str(dev.downLimitedPos))
                    upReached.setChecked(dev.getStateWord(DevAttr.SW_UpperLimit))
                    downReached.setChecked(dev.getStateWord(DevAttr.SW_LowerLimit))
                    if dev.getCtrlWord(DevAttr.CW_Selected):
                        posItem.setBackground(QColor(0, 128, 255))
                        upLimitItem.setBackground(QColor(0, 128, 255))
                        downLimitItem.setBackground(QColor(0, 128, 255))
                        self.cellWidget(rc, 3).setStyleSheet("background-color:#0080ff;")
                    else:
                        posItem.setBackground(QColor(19, 23, 35))
                        upLimitItem.setBackground(QColor(19, 23, 35))
                        downLimitItem.setBackground(QColor(19, 23, 35))
                        self.cellWidget(rc, 3).setStyleSheet("background-color:#131723;")
        except Exception as e:
            print("on Dev Attr value changed", str(e))
class DevDataWidget(QWidget):
    sendDataToTcp = pyqtSignal(str, int, list) # name, id, messageTypeId, action, data
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
        self.subDevLayout = QHBoxLayout()
        for subWidget in self.subDevDataWidgetList:
            s = SubDevDataWidget(subWidget, columnName)
            self.scrollBar.valueChanged.connect(s.verticalScrollBar().setValue)
            self.subDevLayout.addWidget(s)
        self.subDevLayout.addWidget(self.scrollBar)
        self.setLayout(self.subDevLayout)
        self.subDevLayout.setSpacing(0)

    def showEvent(self, QShowEvent):
        li = [TcpServer.Call, TcpServer.SetScreen, {}]
        self.sendDataToTcp.emit(TcpServer.InfoScreen, 0, li) # name, id, messageTypeId, action, data
        pass

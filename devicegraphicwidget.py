#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from tcpserver import *
from devattr import  *
import  json

from miscutils import DeviceInfoWidget, VerticalSlider

class GraphicWidget(QFrame):
    graphicWidgetIndex = pyqtSignal(str)
    setVerticalSliderValue = pyqtSignal(int, int, int)
    def __init__(self, index, device, parent=None):
        super().__init__(parent)
        self.devIndex = index
        try:
            self.verticalSlider = VerticalSlider(bottomLimit=device.downLimitedPos, topLimit=device.upLimitedPos, mValue=99999)
            self.setVerticalSliderValue.connect(self.verticalSlider.setFraction)
        except Exception as e:
            print(str(e))
        self.device = device
        self.device.valueChanged.connect(self.onDevAttrValueChanged)
        self.devNameLabel = QLabel(device.devName)
        self.speedNameLabel = QLabel(self.tr("速度:"))
        self.speedLabel = QLabel("****")
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.speedNameLabel)
        hLayout.addWidget(self.speedLabel)
        hLayout.setAlignment(Qt.AlignLeft)
        layout = QVBoxLayout()
        layout.addWidget(self.devNameLabel, alignment=Qt.AlignHCenter)
        layout.addLayout(hLayout)
        layout.addWidget(self.verticalSlider)
        self.setLayout(layout)
        # self.setFrameShape(QFrame.Box)

    def leaveEvent(self, *args, **kwargs):
        self.graphicWidgetIndex.emit("")

    def onDevAttrValueChanged(self, id, name):
        try:
            dev = self.sender()
            if not isinstance(dev, DevAttr):
                return
            self.setVerticalSliderValue.emit(dev.currentPos, dev.upLimitedPos, dev.downLimitedPos)
        except Exception as e:
            print("onDevAttrValue changed", str(e))

    def enterEvent(self, *args, **kwargs):
        self.graphicWidgetIndex.emit(self.devNameLabel.text())

class DeviceGraphicWidget(QWidget):
    showDeviceInformation = pyqtSignal(str)
    sendDataToTcp = pyqtSignal(str, int, list) # name, id, messageTypeId, action, data
    def __init__(self, subDevList=[], parent=None):
        super().__init__(parent)
        self.subDevList = subDevList
        self.operateDevList = {}
        self.deviceInfoWidget = DeviceInfoWidget(self)
        self.showDeviceInformation.connect(self.deviceInfoWidget.onDeviceInformation)
        self.showDeviceInfoTimer = QTimer()
        self.showDeviceInfoTimer.timeout.connect(self.onShowDeviceInfoTimerTimeout)
        self.scrollArea = QScrollArea(self)
        self.tipsLabel = QLabel("请在触摸屏上选择设备，并点击确认...")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.tipsLabel)
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)
        self.showDevGraphic()
    def showDevGraphic(self, devList=[]):
        try:
            column = 0
            row = 0
            count = 0
            layout = QGridLayout()
            layout.setSpacing(0)
            for dev in devList:
                if column > 10:
                    column = 0
                    row += 1
                gWidget = GraphicWidget(count, dev)
                gWidget.graphicWidgetIndex.connect(self.onGraphicWidgetIndex)
                layout.addWidget(gWidget, row, column)
                column += 1
                count += 1
            widget = QWidget()
            widget.setLayout(layout)
            self.scrollArea.setWidget(widget)
            self.sendDevToInfoScreen()
            self.broadCastSelectedDev()
        except Exception as e:
            print("show dev graphic", str(e))
    def broadCastSelectedDev(self):
        for sec, devList in self.operateDevList.items():
            info = {
                "Section": sec,
                "Device": devList
            }
            li = [TcpServer.Call, TcpServer.DeviceStateChanged, info]
            for i in range(4): # Fixme: 由服务器来广播会更好
                self.sendDataToTcp.emit(TcpServer.TouchScreen, i, li)
    def sendDevToInfoScreen(self):
        for sec, devList in self.operateDevList.items():
            devListInfo = []
            sec %= 4 # maximum screen in infoscreen
            for dev in devList:
                devListInfo.append(dev)
            info = {"Modal": "Single",
                    "Running": False,
                    "Section": sec,
                    "SceneName": [],
                    "Device": devListInfo}
            li = [TcpServer.Call, TcpServer.SetScreenValue, info]
            self.sendDataToTcp.emit(TcpServer.InfoScreen, 0, li) # name, id, messageTypeId, action, data
    def onGraphicWidgetIndex(self, devName):
        if devName:
            self.showDeviceInfoTimer.start(1000)
            self.showDeviceInformation.emit(devName)
        else:
            self.showDeviceInfoTimer.stop()
            if not self.deviceInfoWidget.frameGeometry().contains(QCursor.pos()):
                self.deviceInfoWidget.hide()

    def onShowDeviceInfoTimerTimeout(self):
        self.showDeviceInfoTimer.stop()
        self.deviceInfoWidget.show()
        self.deviceInfoWidget.raise_()

    @pyqtSlot(int, list)
    def onUpdateDeviceState(self, sec, devList):
        try:
            devAttrList = []
            if sec == -1:
                self.operateDevList = {}
            else:
                if sec in self.operateDevList.keys(): # 清除旧数据
                    for oldDev in self.operateDevList[sec]:
                        for devInfo in DevAttr.devAttrList:
                            if devInfo.devName == oldDev[0]:
                                devInfo.clearCtrlWord(DevAttr.CW_Selected)
                                devInfo.section = -1
                self.operateDevList[sec] = devList
                for sec in self.operateDevList.keys():
                    for dev in self.operateDevList[sec]:
                        for devInfo in DevAttr.devAttrList:
                            if devInfo.devName == dev[0] and dev[1] == 1:
                                devInfo.setCtrlWord(DevAttr.CW_Selected)
                                devInfo.section = sec
                                devAttrList.append(devInfo)
            self.showDevGraphic(devAttrList)
        except Exception as e:
            print("onUpdateDeviceState", str(e))

    def showEvent(self, QShowEvent):
        li = [TcpServer.Call, TcpServer.SetScreen, {}]
        self.sendDataToTcp.emit(TcpServer.InfoScreen, i, li)
        self.sendDevToInfoScreen()
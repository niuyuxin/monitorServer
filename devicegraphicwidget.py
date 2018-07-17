#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from miscutils import DeviceInfoWidget, VerticalSlider


class GraphicWidget(QFrame):
    graphicWidgetIndex = pyqtSignal(str)

    def __init__(self, index, device=None, parent=None):
        super().__init__(parent)
        self.devIndex = index
        try:
            self.verticalSlider = VerticalSlider(bottomLimit=10000, topLimit=90000, mValue=99999)
        except Exception as e:
            print(str(e))
        self.devNameLabel = QLabel(self.tr(device))
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

    def enterEvent(self, *args, **kwargs):
        self.graphicWidgetIndex.emit(self.devNameLabel.text())

class DeviceGraphicWidget(QWidget):
    showDeviceInformation = pyqtSignal(str)
    def __init__(self, subDevList=[], parent=None):
        super().__init__(parent)
        self.subDevList = subDevList
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
        self.showDevGraphic(devList=[])
    def showDevGraphic(self, devList):
        column = 0
        row = 0
        count = 0
        layout = QGridLayout()
        layout.setSpacing(0)
        for subDev in devList:
            if column > 10:
                column = 0
                row += 1
            gWidget = GraphicWidget(count, subDev)
            gWidget.graphicWidgetIndex.connect(self.onGraphicWidgetIndex)
            layout.addWidget(gWidget, row, column)
            column += 1
            count += 1
        widget = QWidget()
        widget.setLayout(layout)
        self.scrollArea.setWidget(widget)
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

    def onSelectedDevice(self, devList):
        self.showDevGraphic(devList)
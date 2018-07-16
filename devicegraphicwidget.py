#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from miscutils import DeviceInfoWidget, VerticalSlider


class GraphicWidget(QFrame):
    graphicWidgetIndex = pyqtSignal(int)

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
        self.graphicWidgetIndex.emit(-1)

    def enterEvent(self, *args, **kwargs):
        self.graphicWidgetIndex.emit(self.devIndex)


class DeviceGraphicWidget(QWidget):
    showDeviceInformation = pyqtSignal(str)
    def __init__(self, subDevList=[], parent=None):
        super().__init__(parent)
        self.subDevList = subDevList
        self.deviceInfoWidget = DeviceInfoWidget()
        self.showDeviceInformation.connect(self.deviceInfoWidget.onDeviceInformation)
        self.showDeviceInfoTimer = QTimer()
        self.showDeviceInfoTimer.timeout.connect(self.onShowDeviceInfoTimerTimeout)
        self.scrollLayout = QGridLayout()
        self.scrollLayout.setSpacing(0)
        column = 0
        row = 0
        count = 0
        for subDev in self.subDevList:
            if column > 10:
                column = 0
                row += 1
            gWidget = GraphicWidget(count, subDev)
            gWidget.graphicWidgetIndex.connect(self.onGraphicWidgetIndex)
            self.scrollLayout.addWidget(gWidget, row, column)
            column += 1
            count += 1
        self.scrollWidget = QWidget(self)
        # self.scrollWidget.setWindowFlags(Qt.SubWindow)
        # self.scrollWidget.showFullScreen()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

    def onGraphicWidgetIndex(self, index):
        if index != -1:
            self.showDeviceInfoTimer.start(3000)
            self.showDeviceInformation.emit(self.subDevList[index])
        else:
            if not self.deviceInfoWidget.frameGeometry().contains(QCursor.pos()):
                self.deviceInfoWidget.hide()
            self.showDeviceInfoTimer.stop()

    def onShowDeviceInfoTimerTimeout(self):
        self.showDeviceInfoTimer.stop()
        self.deviceInfoWidget.show()

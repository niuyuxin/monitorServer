#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from verticalslider import *

class GraphicWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        try:
            verticalSlider = VerticalSlider(bottomLimit=10000, topLimit=90000, mValue=99999)
        except Exception as e:
            print(str(e))
        layout = QHBoxLayout()
        layout.addWidget(verticalSlider)
        self.setLayout(layout)
class DeviceGraphicWidget(QWidget):
    def __init__(self, subDevList = [], parent = None):
        super().__init__(parent)
        self.scrollLayout = QGridLayout()
        self.scrollLayout.setSpacing(0)
        column = 0
        row = 0
        for subDev in subDevList:
            if column > 10:
                column = 0
                row += 1
            gWidget = GraphicWidget()
            self.scrollLayout.addWidget(gWidget, row, column)
            column += 1

        self.scrollWidget = QWidget(self)
        self.scrollWidget.setWindowFlags(Qt.SubWindow)
        self.scrollWidget.showFullScreen()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidget(self.scrollWidget)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

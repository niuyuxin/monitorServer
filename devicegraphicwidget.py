#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Slider(QSlider):
    def __init__(self):
        super().__init__()
        self.setOrientation(Qt.Vertical)
class DeviceGraphicWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.slider = Slider()
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.slider)
        self.setLayout(self.layout)

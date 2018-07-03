#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SubDevDataWidget(QTableWidget):
    def __init__(self, row = [], column = [], parent = None):
        super().__init__(parent)
        self.setColumnCount(len(column))
        self.setRowCount(len(row))
        upCheckBox = QCheckBox("上")
        downCheckBox = QCheckBox("下")
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(upCheckBox)
        layout.addWidget(downCheckBox)
        widget.setLayout(layout)
        widget.showFullScreen()
        self.setCellWidget(0, 3, widget)
        self.horizontalHeader().setStyleSheet("QHeaderView::section{background:skyblue;}")
        self.setHorizontalHeaderLabels(column)
        self.setVerticalHeaderLabels(row)
        self.setAutoScroll(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
class DevDataWidget(QWidget):
    def __init__(self, subDevList = [], parent = None):
        super().__init__(parent)
        self.hLayout = QHBoxLayout()
        self.widget = QWidget(self)
        self.subDevDataWidgetList = []
        columnName = [self.tr("实际位置"), self.tr("上软限"), self.tr("下软限"), self.tr("限位开关")]
        subWidgetList = []
        row = []
        count = 0
        perSubWidgetDevNumber = len(subDevList)/4
        if len(subDevList)%4 != 0:
            perSubWidgetDevNumber += 1
        for dev in subDevList:
            if count % perSubWidgetDevNumber == 0:
                if len(row) != 0:
                    subWidgetList.append(row)
                row = []
            row.append(dev)
            count += 1
        subWidgetList.append(row)
        self.scrollBar = QScrollBar()
        self.scrollBar.setRange(0, perSubWidgetDevNumber)
        for subWidget in subWidgetList:
            s = SubDevDataWidget(subWidget, columnName)
            self.scrollBar.valueChanged.connect(s.verticalScrollBar().setValue)
            self.subDevDataWidgetList.append(s)
            self.hLayout.addWidget(s)
        self.hLayout.addWidget(self.scrollBar)
        self.setLayout(self.hLayout)
        self.hLayout.setSpacing(0)





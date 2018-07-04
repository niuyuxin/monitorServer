#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DevInforWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("information widget")
        self.setFocus(Qt.MouseFocusReason)
        self.setMouseTracking(True)
        self.devNameLabel = QLabel("设备名称")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.devNameLabel)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.hide()
    def showEvent(self, QShowEvent):
        try:
            width = qApp.desktop().screenGeometry().width()
            height = qApp.desktop().screenGeometry().height()
            if QCursor.pos().x() + self.frameGeometry().width() > width:
                self.move(QCursor.pos() - QPoint(self.frameGeometry().width(), self.frameGeometry().height()))
            elif QCursor.pos().y() + self.frameGeometry().height() > height:
                self.move(QCursor.pos()-QPoint(self.frameGeometry().width(), self.frameGeometry().height()))
            else:
                self.move(QCursor.pos())
        except Exception as e:
            print(str(e))
    # def leaveEvent(self, QEvent): # Fixme: it doesn't work.
    #     self.hide()
    #     print(">>>")
    def focusOutEvent(self, QFocusEvent): # Fixme: when widget lost focus, hide it.
        self.hide()

class SubDevDataWidget(QTableWidget):
    def __init__(self, row = [], column = [], parent = None):
        super().__init__(parent)
        self.devInformationWidget = DevInforWidget()
        self.mouseInRow = -1
        self.mouseInColumn = 0
        self.setColumnCount(len(column))
        self.setRowCount(len(row))
        self.horizontalHeader().setStyleSheet("QHeaderView::section{background:skyblue;}")
        self.setHorizontalHeaderLabels(column)
        self.setVerticalHeaderLabels(row)
        try: # try to create sub contents
            for i in range(len(row)):
                upCheckBox = QCheckBox("上限")
                downCheckBox = QCheckBox("下限")
                widget = QWidget()
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
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setMouseTracking(True) # should turn on mouse tracking when user cell entered
        self.cellEntered.connect(self.onCellEntered)
        # tigger informatin display
        self.triggerInfoDisplayTimer = QTimer()
        self.triggerInfoDisplayTimer.timeout.connect(self.onTriggerInfoDisplayTimerTimeout)

    def onCellEntered(self, row, column):
        if row != self.mouseInRow:
            self.triggerInfoDisplayTimer.start(1000)
            self.devInformationWidget.hide()
            self.mouseInRow = row
    def enterEvent(self, *args, **kwargs):
        pass # print("enter")
    def leaveEvent(self, *args, **kwargs):
        if not self.devInformationWidget.frameGeometry().contains(QCursor.pos()):
            self.devInformationWidget.hide()
        self.triggerInfoDisplayTimer.stop()
    def onTriggerInfoDisplayTimerTimeout(self):
        self.triggerInfoDisplayTimer.stop()
        self.devInformationWidget.show()
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





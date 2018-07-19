#!/usr/bin/env python3


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DeviceContainer(QFrame):
    def __init__(self, devList=None, parent=None):
        super().__init__(parent)
        self.widgetList = []
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignRight)
        pixMap = QPixmap(":/images/images/dirpic.jpg")
        for dev in devList:
            labelP = QLabel(dev)
            labelP.setFrameShape(QFrame.Box)
            labelP.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            labelS = QLabel("电机")
            labelS.setFrameShape(QFrame.Box)
            layout = QHBoxLayout()
            layout.addWidget(labelP)
            layout.addWidget(labelS)
            self.mainLayout.addLayout(layout)
            labelP.setMaximumSize(100, 100)
            labelS.setMaximumSize(40,40)
            self.widgetList.append(labelP)
        self.mainLayout.setContentsMargins(20,5,5,5)
        self.setLayout(self.mainLayout)
    def paintEvent(self, QPaintEvent):
        rect = self.geometry()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.black);
        painter.drawLine(0, 0, 0, self.widgetList[-1].pos().y()+self.widgetList[-1].height()/2)
        for w in self.widgetList:
            painter.drawLine(0, w.pos().y()+w.height()/2, w.pos().x(), w.pos().y()+w.height()/2)
            painter.drawLine(w.pos().x()+w.width(), w.pos().y() + w.height() / 2, w.pos().x()+w.width()+6, w.pos().y() + w.height() / 2)
            if True: # draw x
                painter.drawLine(w.pos().x()/2-5, w.pos().y()+w.height()/3,
                                 w.pos().x()/2+10, w.pos().y()+w.height()*3/4)
                painter.drawLine(w.pos().x() / 2+10, w.pos().y() + w.height() / 3,
                                     w.pos().x() / 2-5, w.pos().y() + w.height() * 3 / 4)

class DeviceNetGraphic(QWidget):
    def __init__(self, devList=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graphic...")
        self.titleLabel = QLabel("Graphic.... add some words in here")
        self.serverLabel = QLabel("Server pic", self)
        self.serverLabel.setObjectName("serverLabel")
        self.serverLabel.setFrameShape(QFrame.Box)
        self.serverLabel.setFixedSize(100, 100)
        self.plcLabel = QLabel("Plc pic", self)
        self.plcLabel.setObjectName("plcLabel")
        self.plcLabel.setFrameShape(QFrame.Panel)
        self.plcLabel.setFixedSize(70, 70)
        self.devLabelList = []
        self.devFrame = QFrame(self)
        self.devLayout = QHBoxLayout()
        for i in range(10):
            devList = []
            for d in range(10):
                devList.append("变频器{}".format(i*10+d))
            dev = DeviceContainer(devList=devList)
            self.devLayout.addWidget(dev)
        self.devLayout.setContentsMargins(0,0,0,0)
        self.devFrame.setLayout(self.devLayout)
        self.exitPushButton = QPushButton("退出")
        self.exitPushButton.clicked.connect(self.close)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.serverLabel, alignment=Qt.AlignHCenter)
        self.mainLayout.addWidget(self.plcLabel, alignment=Qt.AlignHCenter)
        self.mainLayout.addWidget(self.devFrame)
        self.mainLayout.addWidget(self.exitPushButton, alignment=Qt.AlignHCenter)
        self.mainLayout.setSpacing(40)
        self.setLayout(self.mainLayout)

    def paintEvent(self, QPaintEvent):
        rect = self.geometry()
        # self.serverLabel.move(rect.width()/2-self.serverLabel.width()/2, DeviceNetGraphic.UPMARGIN)
        # self.plcLabel.move(rect.width()/2-self.plcLabel.width()/2, self.serverLabel.height()*1.5+DeviceNetGraphic.UPMARGIN)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.black);
        painter.drawLine(QPointF(rect.width()//2, self.serverLabel.pos().y() + self.serverLabel.height()),
                         QPointF(rect.width()//2, self.plcLabel.pos().y()))
        painter.drawLine(QPointF(rect.width()//2, self.plcLabel.pos().y()+self.plcLabel.height()),
                         QPointF(rect.width()//2, self.devFrame.pos().y()))
        # self.devFrame.move(rect.width()//2-self.devFrame.width()/2, self.plcLabel.pos().y()+self.plcLabel.height()+DeviceNetGraphic.UPMARGIN)
        painter.setPen(Qt.black)
        painter.drawLine(self.devFrame.pos().x(), self.devFrame.pos().y(),
                         self.devFrame.pos().x() + self.devFrame.width(), self.devFrame.pos().y())


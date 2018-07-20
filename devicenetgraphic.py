#!/usr/bin/env python3


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import  time
class DeviceContainer(QFrame):
    TOPMARGIN = 30
    def __init__(self, devList=None, parent=None):
        super().__init__(parent)
        self.mainLayout = QHBoxLayout()
        self.devLabelList = []
        if devList:
            self.createDev(devList)
    def deleteDev(self):
        while self.mainLayout.itemAt(0):
            item = self.mainLayout.takeAt(0)
            while item.itemAt(0):
                subItem = item.takeAt(0)
                while subItem.itemAt(0):
                    label = subItem.takeAt(0).widget()
                    label.setParent(None)
                    # del label
                # del subItem
            # del item

    def createDev(self, devList):
        self.deleteDev()
        rowCount = 0
        colCount = 0
        colCountNumber = (len(devList)//14 + 1)
        for dev in devList:
            if colCount == 0:
                secLayout = QVBoxLayout()
                secLayout.setContentsMargins(30, 0, 0, 0)
                self.mainLayout.addLayout(secLayout)
            pLabel = QLabel(dev)
            pLabel.setTextFormat(Qt.PlainText)
            pLabel.setFrameShape(QFrame.Box)
            pLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            sLabel = QLabel("电机")
            sLabel.setFrameShape(QFrame.Box)
            pLabel.setMaximumSize(100, 100)
            sLabel.setMaximumSize(40,40)
            tLayout = QHBoxLayout()
            tLayout.addWidget(pLabel)
            tLayout.addWidget(sLabel)
            tLayout.setContentsMargins(0, 0, 0, 0)
            secLayout.addLayout(tLayout)
            colCount += 1
            if colCount >= colCountNumber:
                colCount = 0
                rowCount = 0
            self.devLabelList.append(pLabel)
        self.mainLayout.setContentsMargins(0,DeviceContainer.TOPMARGIN,0,0)
        self.setLayout(self.mainLayout)
    def stateChanged(self, devName, state, working):
        for dev in self.devLabelList:
            if dev.text() == devName:
                dev.setEnabled(state)
                if working and state:
                    dev.setTextFormat(Qt.RichText)
                else:
                    dev.setTextFormat(Qt.PlainText)
        self.update()
    def paintEvent(self, QPaintEvent):
        widgetRect = self.contentsRect()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.black);
        for count in range(self.mainLayout.count()):
            groupLayout = self.mainLayout.itemAt(count)
            rect = groupLayout.contentsRect()
            rectLeftMargin = groupLayout.getContentsMargins()[0]
            painter.drawLine(rect.x()-rectLeftMargin, widgetRect.y(),
                             rect.x()-rectLeftMargin, widgetRect.y()+widgetRect.height())
            for gCount in range(groupLayout.count()):
                labelLayout = groupLayout.itemAt(gCount)
                labelRect = labelLayout.contentsRect()
                painter.setPen(Qt.black);
                if labelLayout.count() == 2:
                    labelA = labelLayout.itemAt(0).widget()
                    labelB = labelLayout.itemAt(1).widget()
                    painter.drawLine(rect.x()-rectLeftMargin, labelRect.y() + labelRect.height() / 2,
                                     labelA.pos().x(), labelRect.y() + labelRect.height() / 2)
                    painter.drawLine(labelA.pos().x() + labelA.width(), labelRect.y() + labelRect.height() / 2,
                                     labelB.pos().x(), labelRect.y() + labelRect.height() / 2)
                    if not labelA.isEnabled(): # draw x
                        painter.setPen(Qt.darkRed)
                        painter.drawLine(labelA.pos().x() - rectLeftMargin/2 - 5, labelA.pos().y()+labelA.height()/3,
                                         labelA.pos().x() - rectLeftMargin/2 + 5, labelA.pos().y()+labelA.height()*2/3)
                        painter.drawLine(labelA.pos().x() - rectLeftMargin/2 + 5, labelA.pos().y() + labelA.height()/3,
                                         labelA.pos().x() - rectLeftMargin/2 - 5, labelA.pos().y() + labelA.height()*2/3)

class DeviceNetGraphic(QDialog):
    def __init__(self, devList=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Graphic...")
        self.titleLabel = QLabel("Graphic.... add some words in here")
        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.serverLabel = QLabel("Server Picture", self)
        self.serverLabel.setObjectName("serverLabel")
        self.serverLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.serverLabel.setFrameShape(QFrame.StyledPanel)
        self.serverLabel.setFixedSize(100, 100)
        self.plcLabel = QLabel("Plc Picture", self)
        self.plcLabel.setObjectName("plcLabel")
        self.plcLabel.setFrameShape(QFrame.StyledPanel)
        self.plcLabel.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.plcLabel.setFixedSize(80, 80)
        self.devFrame = DeviceContainer(devList)
        self.exitPushButton = QPushButton("退出")
        self.exitPushButton.clicked.connect(self.close)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.serverLabel, alignment=Qt.AlignHCenter)
        self.mainLayout.addWidget(self.plcLabel, alignment=Qt.AlignHCenter)
        self.mainLayout.addWidget(self.devFrame)
        self.mainLayout.addWidget(self.exitPushButton, alignment=Qt.AlignRight)
        self.mainLayout.setSpacing(40)
        self.setLayout(self.mainLayout)
    def stateChanged(self, devName, state, working=False):
        self.devFrame.stateChanged(devName, state, working)
    def paintEvent(self, QPaintEvent):
        rect = self.geometry()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.black);
        painter.drawLine(QPointF(rect.width()//2, self.serverLabel.pos().y() + self.serverLabel.height()),
                         QPointF(rect.width()//2, self.plcLabel.pos().y()))
        painter.drawLine(QPointF(rect.width()//2, self.plcLabel.pos().y()+self.plcLabel.height()),
                         QPointF(rect.width()//2, self.devFrame.pos().y()))
        painter.setPen(Qt.black)
        painter.drawLine(self.devFrame.pos().x(), self.devFrame.pos().y(),
                         self.devFrame.pos().x() + self.devFrame.width(), self.devFrame.pos().y())


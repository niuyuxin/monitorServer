#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class DeviceInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("设备详细信息"))
        self.setFocus(Qt.MouseFocusReason)
        self.setMouseTracking(True)
        self.deviceNameLabel = QLabel("***")
        self.deviceUpLimit = QLabel(self.tr("已到达上限"))
        self.deviceDownLimit = QLabel(self.tr("已到达下限"))
        self.devLimitLayout = QHBoxLayout()
        self.devLimitLayout.addWidget(self.deviceUpLimit)
        self.devLimitLayout.addWidget(self.deviceDownLimit)
        self.deviceCurPosLabel = QLabel(self.tr("当前位置:"))
        self.devCurPosLineEdit = QLineEdit()
        self.devCurPosLineEdit.setFocusPolicy(Qt.NoFocus)
        self.devCurPosLineEdit.setEnabled(False)
        self.devCurPosLayout = QHBoxLayout()
        self.devCurPosLayout.addWidget(self.deviceCurPosLabel)
        self.devCurPosLayout.addWidget(self.devCurPosLineEdit)
        self.devWarningMesLabel = QLabel(self.tr("报警信息故障字:"))
        self.devWarningMesLineEdit = QLineEdit()
        self.devWarningMesLineEdit.setFocusPolicy(Qt.NoFocus)
        self.devWarningMesLineEdit.setEnabled(False)
        self.devWaringMesLayout = QHBoxLayout()
        self.devWaringMesLayout.addWidget(self.devWarningMesLabel)
        self.devWaringMesLayout.addWidget(self.devWarningMesLineEdit)
        self.devCompilingLabel = QLabel(self.tr("是否有编场设置:"))
        self.devCompilingInfoLabel = QLabel(self.tr(self.tr("未知")))
        self.devCompilingLayout = QHBoxLayout()
        self.devCompilingLayout.addWidget(self.devCompilingLabel)
        self.devCompilingLayout.addWidget(self.devCompilingInfoLabel)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.deviceNameLabel, alignment=(Qt.AlignHCenter|Qt.AlignTop))
        self.layout.addLayout(self.devLimitLayout)
        self.layout.addLayout(self.devCurPosLayout)
        self.layout.addLayout(self.devWaringMesLayout)
        self.layout.addLayout(self.devCompilingLayout)
        self.setLayout(self.layout)
        self.setFixedSize(self.sizeHint())
        self.setWindowFlags((self.windowFlags()&~Qt.WindowMinimizeButtonHint)|Qt.Window)
        self.setFocusPolicy(Qt.WheelFocus)
        self.setFocus(Qt.MenuBarFocusReason)
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
    # def focusInEvent(self, QFocusEvent):
    #     pass
    # def enterEvent(self, QEvent):
    #     pass
    def leaveEvent(self, QEvent): # Fixme: it doesn't work.
        self.hide()
    def focusOutEvent(self, QFocusEvent): # Fixme: when widget lost focus, hide it.
        self.hide()
    def onDeviceInformation(self, device): # Fixme, the type of device should be 'subDev' type, to do define it.
        self.deviceNameLabel.setText(device)

class VerticalSlider(QWidget):
    XMARGIN = 5
    YMARGIN = 10.0
    WSTRING = "**********"
    CYLINDERWIDTH = 10
    BOTTOMLIMITLEN = 10
    TOPLIMITLEN = 10
    TOPMARGIN = 20.0
    BOTTOMMARGIN = 20.0
    valueChanged = pyqtSignal(int, int)
    def __init__(self, name = None, topLimit = None, bottomLimit = None, act =0, mValue=10, parent=None):
        super().__init__(parent)
        self.actValue = act
        self.maxValue = mValue
        if topLimit > bottomLimit and topLimit < mValue:
            self.topLimit = topLimit
            self.bottomLimit = bottomLimit
        else:
            raise ValueError("topLimit or bottomLimit error")
        self.devName = name
        self.setFocusPolicy(Qt.WheelFocus)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
    def sizeHint(self):
        return self.minimumSizeHint()
    def minimumSizeHint(self):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() - 1)
        fm = QFontMetricsF(font)
        return QSize(VerticalSlider.XMARGIN*26+fm.height(), VerticalSlider.TOPMARGIN + fm.height()  * 15)

    def setFraction(self, actValue, maxValue=None):
        if maxValue is not None:
            if 3 <= maxValue <= 99999:
                self.maxValue = maxValue
            else:
                raise ValueError("denominator out of range")
        if 0 <= actValue <= self.maxValue:
            self.actValue = actValue
        else:
            raise ValueError("numerator out of range")
        self.topLimit = float(0.7)*self.maxValue
        self.bottomLimit = float(0.3)*self.maxValue
        self.update()
        self.updateGeometry()

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.moveSlider(event.y())
    #         event.accept()
    #     else:
    #         QWidget.mousePressEvent(self, event)

    # def mouseMoveEvent(self, event):
    #     self.moveSlider(event.y())

    def moveSlider(self, x):
        span = self.height() - VerticalSlider.TOPMARGIN - VerticalSlider.BOTTOMMARGIN
        offset = span + VerticalSlider.TOPMARGIN - x
        actValue = self.maxValue - int(round(self.maxValue * (1.0 - (offset / span))))
        actValue = max(0, min(actValue, self.maxValue))
        if actValue != self.actValue:
            self.actValue = actValue
            self.valueChanged.emit(self.actValue, self.maxValue)
            self.update()

    def paintEvent(self, event=None):
        font = QFont(self.font())
        font.setPointSize(font.pointSize() + 1)
        fm = QFontMetricsF(font)
        # fracWidth = fm.width(VerticalSlider.WSTRING)
        # indent = fm.boundingRect("9").width() / 2.0
        # # if not X11:
        # #     fracWidth *= 1.5
        span = self.height() - VerticalSlider.TOPMARGIN - VerticalSlider.BOTTOMMARGIN
        percentOfRemainValue = (float(self.maxValue)-self.actValue) / float(self.maxValue)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setPen(self.palette().color(QPalette.Mid))
        painter.setBrush(self.palette().brush(QPalette.AlternateBase))
        painter.drawRect(self.rect())

        segColor = QColor(Qt.blue).darker(100)  # draw rule
        segLineColor = segColor.darker()
        painter.setPen(segLineColor)
        painter.setBrush(self.palette().brush(QPalette.AlternateBase))
        painter.drawRect(VerticalSlider.XMARGIN, VerticalSlider.TOPMARGIN,
                         VerticalSlider.CYLINDERWIDTH, span)
        textColor = self.palette().color(QPalette.Text)
        segWidth = VerticalSlider.XMARGIN * 4
        segHeight = span / self.maxValue
        nRect = fm.boundingRect(VerticalSlider.WSTRING)
        y = VerticalSlider.TOPMARGIN
        xOffset = segHeight + fm.height()
        for i in range(10+1):
            painter.setPen(segLineColor)
            painter.drawLine(VerticalSlider.XMARGIN*4, y, segWidth + 3, y)
            y += span/10
        span = int(span)
        x = VerticalSlider.XMARGIN*7 # draw triangle
        triangle = [QPointF(x, percentOfRemainValue * span + VerticalSlider.TOPMARGIN - 5),
                    QPointF(x, (percentOfRemainValue * span) + VerticalSlider.TOPMARGIN + 5),
                    QPointF(segWidth, (percentOfRemainValue * span) + VerticalSlider.TOPMARGIN)]
        painter.setPen(Qt.red)
        painter.setBrush(Qt.darkYellow)
        painter.drawPolygon(QPolygonF(triangle))

        painter.setPen(segLineColor)
        painter.drawLine(x, (percentOfRemainValue * span) + VerticalSlider.TOPMARGIN,
                         x+10, (percentOfRemainValue * span) + VerticalSlider.TOPMARGIN)

        painter.setPen(Qt.red) # draw frame
        painter.setBrush(self.palette().brush(QPalette.AlternateBase))
        painter.drawRect(x+10, VerticalSlider.TOPMARGIN + (percentOfRemainValue * span) - 8, 50, 15)

        topLimitPercent = (self.maxValue - self.topLimit)/float(self.maxValue)
        bottomLimitPercent = (self.maxValue - self.bottomLimit)/float(self.maxValue)
        painter.drawLine(VerticalSlider.XMARGIN*4, (topLimitPercent * span) + VerticalSlider.TOPMARGIN,
                         x+15, (topLimitPercent * span) + VerticalSlider.TOPMARGIN)
        painter.drawLine(VerticalSlider.XMARGIN*4, (bottomLimitPercent * span) + VerticalSlider.TOPMARGIN,
                         x+15, (bottomLimitPercent * span) + VerticalSlider.TOPMARGIN)

        rect = QRectF(nRect)
        painter.setPen(textColor)
        rect.moveCenter(QPointF(x+35, (percentOfRemainValue * span) + VerticalSlider.TOPMARGIN))
        painter.drawText(rect, Qt.AlignCenter, "{}mm".format(self.actValue))
        rect.moveCenter(QPointF(x + 55, (topLimitPercent * span) + VerticalSlider.TOPMARGIN))
        painter.drawText(rect, Qt.AlignCenter, "{}:{}".format(self.tr("上软限"), int(self.topLimit)))

        rect.moveCenter(QPointF(VerticalSlider.XMARGIN*6, VerticalSlider.TOPMARGIN - 10))
        if self.actValue == self.maxValue:
            painter.fillRect(rect, QBrush(Qt.red))
        painter.drawText(rect, Qt.AlignCenter, self.tr("上限位开关"))
        rect.moveCenter(QPointF(x + 55, (bottomLimitPercent * span) + VerticalSlider.TOPMARGIN))
        painter.drawText(rect, Qt.AlignCenter, "{}:{}".format(self.tr("下软限"), int(self.bottomLimit)))
        rect.moveCenter(QPointF(VerticalSlider.XMARGIN*6, span + VerticalSlider.TOPMARGIN + 10))
        if self.actValue == 0:
            painter.fillRect(rect, QBrush(Qt.red))
        painter.drawText(rect, Qt.AlignCenter, self.tr("下限位开关"))

        if self.actValue > self.topLimit:
            painter.setPen(QColor(Qt.red))  # draw cylinder
            painter.setBrush(QColor(Qt.red).darker())
        elif self.actValue < self.bottomLimit:
            painter.setPen(QColor(Qt.green)) # draw cylinder
            painter.setBrush(QColor(Qt.green).darker())
        else:
            painter.setPen(segLineColor) # draw cylinder
            painter.setBrush(segColor)
        painter.drawRect(VerticalSlider.XMARGIN, VerticalSlider.TOPMARGIN,
                         VerticalSlider.CYLINDERWIDTH, percentOfRemainValue*span)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    slider = VerticalSlider(topLimit=99999*0.8, bottomLimit=99999*0.2, mValue=99999)
    slider.show()
    app.exec_()


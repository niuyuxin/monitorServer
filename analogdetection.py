#!/usr/bin/env python3

from PyQt5.QtCore import *
from ctypes import *
import time


class inputValueType(Structure):
    _fields_ = [('val', c_int)]

class AnalogDetection(QObject):
    GPIOState = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot()
    def init(self):
        SusiGPIOCtrl = CDLL("Susi4.dll")
        if SusiGPIOCtrl.SusiLibInitialize() == 0:
            print("initialize success")
        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimerTimeout)
        self.timer.start(30)

    def onTimerTimeout(self):
        pass
        # print(QDateTime.currentDateTime().toString("hh:mm:ss.zzz"))


if __name__ == '__main__':
    SusiGPIOCtrl = CDLL("Susi4.dll")
    SusiGPIOCtrl.SusiLibInitialize()
    SusiGPIOCtrl.SusiGPIOSetDirection(7, 1, 1)
    SusiGPIOCtrl.SusiGPIOSetDirection(5, 1, 0)
    SusiGPIOCtrl.SusiGPIOSetDirection(5, 1, 0)
    SusiGPIOCtrl.SusiGPIOSetLevel(6, 1, 1)
    mode = 0
    recordTime = time.time()
    value = inputValueType()
    while True:
        if mode == 0:
            SusiGPIOCtrl.SusiGPIOGetLevel(7, 1, byref(value))
            SusiGPIOCtrl.SusiGPIOSetLevel(5, 1, value.val)
        else:
            SusiGPIOCtrl.SusiGPIOSetLevel(5, 1, 0)
            time.sleep(0.3)
            SusiGPIOCtrl.SusiGPIOSetLevel(5, 1, 1)
            time.sleep(0.3)

        if value.val == 0:
            recordTime = time.time()

        if int(time.time() - recordTime) > 3:
            mode = not mode


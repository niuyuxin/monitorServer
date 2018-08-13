#!/usr/bin/env python3

from PyQt5.QtCore import *
from ctypes import *
import time


class inputValueType(Structure):
    _fields_ = [('val', c_int)]
class AutoFunType(Structure):
    _fields_=[('value',c_int*9)]
class SusiFanControl(Structure):
    _fields_=[('mode',c_int),('pwm',c_int),('autoFan',AutoFunType)]

class AnalogDetection(QObject):
    GPIO_STOP_LED = 3 # 停止程控运行
    GPIO_RUN_LED = 2 # 程控启动灯
    # 数据通信
    GPIO_RUN = 6 # 启动 程控
    GPIO_STOP = 5 # 停止 程控
    GPIO_PROGRAM = 1  # 程控模式
    GPIO_MAINT = 0 # 维保模式
    GPIO_TURN_NEXT =  7 # 下一幕
    GPIO_TURN_PREV = 4 # 上一幕
    KEY_DOWN = 1
    KEY_UP = 0
    LED_ON = 1
    LED_OFF = 0
    GPIO_IN = 1
    GPIO_OUT = 0
    GPIOState = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot()
    def init(self):
        self.SusiCtrl = CDLL("Susi4.dll")
        self.fanCtrl = SusiFanControl()
        self.fanCtrl.mode = 2
        self.fanCtrl.pwm = 0
        self.count = 0
        if self.SusiCtrl.SusiLibInitialize() == 0:
            print("initialize success")
            self.SusiCtrl.SusiFanControlSetConfig(0x22001, byref(self.fanCtrl))
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_RUN_LED, 1, AnalogDetection.GPIO_OUT)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_STOP_LED, 1, AnalogDetection.GPIO_OUT)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_RUN, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_STOP, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_PROGRAM, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_MAINT, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_TURN_NEXT, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_TURN_PREV, 1, AnalogDetection.GPIO_IN)
        self.gpioState = {0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[]}
        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimerTimeout)
        self.timer.start(10)

    def onTimerTimeout(self):
        try:
            if self.count >= 100: self.count = 0
            self.fanCtrl.pwd = self.count
            self.SusiCtrl.SusiFanControlSetConfig(0x22001, byref(self.fanCtrl))
            value = inputValueType()
            for gpio in range(8):
                if gpio in (AnalogDetection.GPIO_RUN_LED, \
                            AnalogDetection.GPIO_STOP_LED): continue
                self.SusiCtrl.SusiGPIOGetLevel(gpio, 1, byref(value))
                if len(self.gpioState[gpio]) < 4:
                    self.gpioState[gpio].append(value.val)
                else:
                    self.gpioState[gpio].pop(0)
                    self.gpioState[gpio].append(value.val)
            for item in self.gpioState.items():
                if item[0] in (AnalogDetection.GPIO_RUN_LED, \
                               AnalogDetection.GPIO_STOP_LED): continue
                if item[1] == [AnalogDetection.KEY_UP,
                               AnalogDetection.KEY_DOWN,
                               AnalogDetection.KEY_DOWN,
                               AnalogDetection.KEY_DOWN]:
                    self.onGPIOState(item[0], True)
                    self.GPIOState.emit(item[0], True)
        except Exception as e:
            print("on timer timeout ", str(e))

    @pyqtSlot(int, int)
    def onGPIOState(self, gpio, state):
        if gpio == AnalogDetection.GPIO_RUN:
            self.SusiCtrl.SusiGPIOSetLevel(AnalogDetection.GPIO_RUN_LED, 1, AnalogDetection.LED_ON)
            self.SusiCtrl.SusiGPIOSetLevel(AnalogDetection.GPIO_STOP_LED, 1, AnalogDetection.LED_OFF)
        elif gpio == AnalogDetection.GPIO_STOP:
            self.SusiCtrl.SusiGPIOSetLevel(AnalogDetection.GPIO_RUN_LED, 1, AnalogDetection.LED_OFF)
            self.SusiCtrl.SusiGPIOSetLevel(AnalogDetection.GPIO_STOP_LED, 1, AnalogDetection.LED_ON)
        print(gpio, state)

    @pyqtSlot(int, int)
    def onAnalogCtrl(self, gpio, s):
        self.onGPIOState(gpio, s)

if __name__ == '__main__':
    SusiCtrl = CDLL("Susi4.dll")
    SusiCtrl.SusiLibInitialize()
    SusiCtrl.SusiGPIOSetDirection(7, 1, 1)
    SusiCtrl.SusiGPIOSetDirection(5, 1, 0)
    SusiCtrl.SusiGPIOSetDirection(6, 1, 0)
    SusiCtrl.SusiGPIOSetLevel(6, 1, 1)
    mode = 0
    recordTime = time.time()
    value = inputValueType()
    while True:
        if mode == 0:
            SusiCtrl.SusiGPIOGetLevel(7, 1, byref(value))
            SusiCtrl.SusiGPIOSetLevel(5, 1, value.val)
        else:
            SusiCtrl.SusiGPIOSetLevel(5, 1, 0)
            time.sleep(0.3)
            SusiCtrl.SusiGPIOSetLevel(5, 1, 1)
            time.sleep(0.3)

        if value.val == 0:
            recordTime = time.time()

        if int(time.time() - recordTime) > 3:
            mode = not mode


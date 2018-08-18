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
    GPIO_STOP_LED = 2 # 停止程控运行
    GPIO_RUN_LED = 3 # 程控启动灯
    # 数据通信
    GPIO_RUN = 7 # 启动 程控
    GPIO_STOP = 4 # 停止 程控
    GPIO_SINGLE = -1 # 单控模式
    GPIO_PROGRAM = 1  # 程控模式
    GPIO_MAINT = 0 # 维保模式
    GPIO_TURN_NEXT =  6 # 下一幕
    GPIO_TURN_PREV = 5 # 上一幕
    KEY_DOWN = 0
    KEY_UP = 1
    LED_ON = 1
    LED_OFF = 0
    GPIO_IN = 1
    GPIO_OUT = 0
    SYS_FUN1_ADDR = 0x22001
    SYS_FUN2_ADDR = 0x23001
    GPIOState = pyqtSignal(int, int)
    ControlModeSwitch = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot()
    def init(self):
        self.SusiCtrl = CDLL("Susi4.dll")
        self.fanCtrl = SusiFanControl()
        self.fanCtrl.mode = 2
        self.count = 0
        if self.SusiCtrl.SusiLibInitialize() == 0:
            print("initialize success")
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_RUN_LED, 1, AnalogDetection.GPIO_OUT)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_STOP_LED, 1, AnalogDetection.GPIO_OUT)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_RUN, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_STOP, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_PROGRAM, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_MAINT, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_TURN_NEXT, 1, AnalogDetection.GPIO_IN)
            self.SusiCtrl.SusiGPIOSetDirection(AnalogDetection.GPIO_TURN_PREV, 1, AnalogDetection.GPIO_IN)
        value = inputValueType()
        self.CtrlMode = -1  # 0 维保模式 1程控模式 -1单控模式
        for gpio in [AnalogDetection.GPIO_PROGRAM, AnalogDetection.GPIO_MAINT]:
            self.SusiCtrl.SusiGPIOGetLevel(gpio, 1, byref(value))
            if value.val == AnalogDetection.KEY_DOWN:
                self.CtrlMode = gpio
                self.ControlModeSwitch.emit(gpio)
        self.gpioState = {0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[]}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.onTimerTimeout)
        self.timer.start(10)

    def onTimerTimeout(self):
        try:
            self.fanCtrl.pwm = (self.count%200)//2
            self.count += 1
            self.SusiCtrl.SusiFanControlSetConfig(AnalogDetection.SYS_FUN1_ADDR, byref(self.fanCtrl))
            self.SusiCtrl.SusiFanControlSetConfig(AnalogDetection.SYS_FUN2_ADDR, byref(self.fanCtrl))
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
                    self.onGPIOState(item[0], AnalogDetection.KEY_DOWN)
                    self.GPIOState.emit(item[0], AnalogDetection.KEY_DOWN)
                elif item[1] == [AnalogDetection.KEY_DOWN,
                                AnalogDetection.KEY_UP,
                                 AnalogDetection.KEY_UP,
                                 AnalogDetection.KEY_UP]:
                    self.onGPIOState(item[0], AnalogDetection.KEY_UP)
                    self.GPIOState.emit(item[0], AnalogDetection.KEY_UP)
        except Exception as e:
            print("on timer timeout ", str(e))

    @pyqtSlot(int, int)
    def onGPIOState(self, gpio, state):
        if gpio in [AnalogDetection.GPIO_PROGRAM, AnalogDetection.GPIO_MAINT]:
            if state == AnalogDetection.KEY_DOWN:
                self.CtrlMode = gpio
            else:
                self.CtrlMode = -1
            self.ControlModeSwitch.emit(self.CtrlMode)
        if self.CtrlMode == AnalogDetection.GPIO_PROGRAM and\
                state == AnalogDetection.KEY_DOWN:
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



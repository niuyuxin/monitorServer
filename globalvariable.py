#/usb/bin/eny python3

from PyQt5.QtCore import *

class DevAttr(QObject):
    SW_UpperLimit = (1<<8)
    SW_LowerLimit = (1<<9)
    CW_Partial = (1<<14)
    CW_Selected = (1<<13)
    CW_Raise = (1<<8)
    CW_Stop = (1<<9)
    CW_Drop = (1<<10)
    valueChanged = pyqtSignal(str, str)
    def __init__(self, id, name, parent=None):
        super().__init__(parent)
        self.currentPos = 0
        self.devName = name
        self.devId = id
        self.ctrlWord = 0
        self.stateWord = 0
        self.upLimitedPos = 0
        self.downLimitedPos = 0
        self.targetPos = 0
        self.zeroPos = 0

    def getStateWord(self, pos):
        return bool(self.stateWord&pos)

    def setStateWord(self, pos):
        self.stateWord |= (pos)

    def clearStateWord(self, pos):
        self.stateWord &= (~pos)

    def setCtrlWord(self, pos):
        self.ctrlWord |= pos

    def clearCtrlWord(self, pos):
        self.ctrlWord &= (~pos)

class GlobalVal():
    UpLimited = 1
    DownLimited = 2
    Speed = 3
    InverterState = 4
    WarningInfo = 5
    Pos = 6
    PlcStateWord = 7
    TargetPos = 8
    monitorSubDevDict = {} # 所有监视器内的设备
    # "devId":["设备名称", "上软限", "下软限", "速度", "变频器状态", "报警信息", "位置", "plc状态字"]
    devInfoList = []
    deviceStateList = {}  # 设备状态列表
    singleCtrlOperation = 0 # 单控运行标志
    singleCtrlSpeed = 0


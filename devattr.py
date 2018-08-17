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
    monitorSubDevDict = {} # 所有监视器内的设备
    devAttrList = []
    singleCtrlOperation = {} # 单控运行标志
    singleCtrlSpeed = {}
    SingleModeD = 0
    SingleModeG = 1
    ProgramMode = 2
    OperationMode = 0
    def __init__(self, id, name, parent=None):
        super().__init__(parent)
        self.currentPos = 0
        self.devName = name
        self.devId = id
        self.ctrlWord = DevAttr.CW_Stop
        self.stateWord = 0
        self.upLimitedPos = 0
        self.downLimitedPos = 0
        self.targetPos = 0
        self.zeroPos = 0
        self.programSetPos = 0
        self.programSetSpeed = 0
        self.programId = ""
        self.section = -1

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


#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import ui_mainwindow
from tcpserver import TcpServer
from devicedatawidget import  DevDataWidget
from deviceprogramwidget import DevProgramWidget
from devicegraphicwidget import  DeviceGraphicWidget
from organizedplay import OrganizedPlay
from database import DataBase
from systemmanagement import *
from devicenetgraphic import *
from plcsocket import *
from devattr import *
from analogdetection import *

class MainWindow(QFrame, ui_mainwindow.Ui_Form):
    plcSocketManagement = pyqtSignal(int)
    getMonitorDevice = pyqtSignal(str, list)
    getPlaysInfo = pyqtSignal()
    sendDataToTcp = pyqtSignal(str, int, list) # name, id, messageTypeId, action, data
    savingParaSetting = pyqtSignal(str, int, int, int)
    analogCtrl = pyqtSignal(int, int)
    # ControlModeSwitch = pyqtSignal(int)
    # PhysicalGPIOState = pyqtSignal(int, int)
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.initMainWindow()
    def initMainWindow(self):
        # create Device Data Widget
        self.devDataWidget = None
        self.devGraphicWidget = None
        self.devProgramWidget  = None
        self.contentWidgetList = []
        # real time object
        self.rtc = QTimer()
        self.rtc.timeout.connect(self.onRtcTimeout)
        self.onRtcTimeout()
        self.rtc.start(1000)
        self.versionLabel.setText(self.getVersion())
        # create mysql database
        self.dataBase = DataBase()
        self.dataBase.getAllDevices(DevAttr.monitorSubDevDict, DevAttr.devAttrList)
        self.dataBase.databaseState.connect(self.onDatabaseState)
        self.dataBaseThread = QThread()
        self.dataBase.moveToThread(self.dataBaseThread)
        self.getMonitorDevice.connect(self.dataBase.onCreateDevicesInfo)
        self.savingParaSetting.connect(self.dataBase.onSavingParaSetting)
        self.dataBaseThread.start()
        # frame
        self.contentFrameLayout = QHBoxLayout()
        self.contentFrame.setLayout(self.contentFrameLayout)
        # self.contentFrameLayout.setContentsMargins(0,0,0,0)
        # graphic view
        self.devGraphicWidget = DeviceGraphicWidget(self.getAllDevice())  # new widget
        self.devGraphicWidget.sendDataToTcp.connect(self.sendDataToTcp)
        self.contentFrameLayout.addWidget(self.devGraphicWidget)
        self.contentWidgetList.append(self.devGraphicWidget)
        # program running..
        self.devProgramWidget = DevProgramWidget()
        self.contentFrameLayout.addWidget(self.devProgramWidget)
        self.contentWidgetList.append(self.devProgramWidget)
        self.devProgramWidget.sendDataToTcp.connect(self.sendDataToTcp)
        self.devProgramWidget.analogCtrl.connect(self.analogCtrl)
        self.showAllDeviceInWidget()
        # create tcp server, main function...
        self.tcpServer = TcpServer()
        self.tcpServerThread = QThread()
        self.tcpServer.moveToThread(self.tcpServerThread)
        self.tcpServer.getAllSubDev.connect(self.onTcpServerGetAllSubDev)
        self.tcpServer.updateDeviceState.connect(self.devGraphicWidget.onUpdateDeviceState)
        self.tcpServer.updateParaSetting.connect(self.onTcpServerUpdateSetting)
        self.tcpServer.operationalCtrl.connect(self.onTcpServerOperationalCtrl)
        self.tcpServer.devConnectingInfo.connect(self.onTcpServerGetDevConnectingInfo)
        self.tcpServer.speedSet.connect(self.onTcpServerSpeedSet)
        self.sendDataToTcp.connect(self.tcpServer.onDataToSend)
        self.tcpServerThread.start()
        # plc Socket
        self.plcSocket = PlcSocket()
        self.plcSocketThread = QThread()
        self.plcSocket.moveToThread(self.plcSocketThread)
        self.plcSocketManagement.connect(self.plcSocket.onTcpSocketManagement)
        self.plcSocketThread.started.connect(self.plcSocket.initTcpSocket)
        self.plcSocketThread.start()
        # analog detection
        self.analogDetection = AnalogDetection()
        self.analogDetectionThread = QThread()
        self.analogDetection.moveToThread(self.analogDetectionThread)
        self.analogDetectionThread.started.connect(self.analogDetection.init)
        self.analogCtrl.connect(self.analogDetection.onAnalogCtrl)
        self.analogDetection.GPIOState.connect(self.onPhysicalGPIOState)
        if not Config.Debug:
            self.analogDetection.ControlModeSwitch.connect(self.onControlModeSwitch)
        self.analogDetectionThread.start()
        # push button signal and slots
        self.dataShowingPushButton.clicked.connect(self.onDataShowingPushButtonClicked)
        self.graphicShowingPushButton.clicked.connect(self.onGraphicShowingPushButtonClicked)
        self.autoRunningPushButton.clicked.connect(self.changeToProgramMode)
        self.organizedPlayPushButton.clicked.connect(self.onOrganizedPlayPushButtonClicked)
        self.systemManagementPushButton.clicked.connect(self.onSystemManagementPushButtonClicked)
        self.netFramePushButton.clicked.connect(self.onNetFramePushButtonClicked)

    def onRtcTimeout(self):
        self.timeLabel.setText(QDateTime.currentDateTime().toString("yyyy/MM/dd dddd hh:mm:ss"))

    @pyqtSlot(str, list)
    def onTcpServerGetAllSubDev(self, monitorName, subDev):
        if DevAttr.monitorSubDevDict.get(monitorName) == subDev:
            print("Got same monitor device!", monitorName)
            return
        if DevAttr.monitorSubDevDict.get(monitorName) is None:
            DevAttr.monitorSubDevDict.setdefault(monitorName, subDev)
        else:
            DevAttr.monitorSubDevDict[monitorName] = subDev
        self.getMonitorDevice.emit(monitorName, subDev)
        print("some thing changed...", subDev)
        DevAttr.devAttrList = self.createDevInfoDict() # 需要等待数据库创建完成以后再生成此变量
        self.showAllDeviceInWidget()

    def getAllDevice(self):
        allDevice = []
        for key in DevAttr.monitorSubDevDict.keys():
            for dev in DevAttr.monitorSubDevDict[key]:
                allDevice.append(dev[1])
        return allDevice

    def createDevInfoDict(self):
        devInfo = []
        for key in DevAttr.monitorSubDevDict.keys():
            for dev in DevAttr.monitorSubDevDict[key]:
                devInfo.append(DevAttr(dev[0], dev[1]))
        return devInfo

    def showAllDeviceInWidget(self):
        if self.devDataWidget is not None:
            self.contentWidgetList.remove(self.devDataWidget)
            self.contentFrameLayout.removeWidget(self.devDataWidget)
            self.devDataWidget.deleteLater()
        self.devDataWidget = DevDataWidget(DevAttr.devAttrList)  # new widget
        self.devDataWidget.sendDataToTcp.connect(self.sendDataToTcp)
        self.contentFrameLayout.addWidget(self.devDataWidget)
        self.contentWidgetList.append(self.devDataWidget)
        self.showWidgetInContentWidget(widget=self.devDataWidget)

    def onDataShowingPushButtonClicked(self):
        DevAttr.OperationMode = DevAttr.SingleModeD
        if self.devDataWidget is not None:
            self.showWidgetInContentWidget(widget=self.devDataWidget)
    def onGraphicShowingPushButtonClicked(self):
        DevAttr.OperationMode = DevAttr.SingleModeG
        self.showWidgetInContentWidget(widget=self.devGraphicWidget)

    def changeToProgramMode(self):
        if Config.Debug:
            DevAttr.OperationMode = DevAttr.ProgramMode
            self.showWidgetInContentWidget(widget=self.devProgramWidget)

    @pyqtSlot(int)
    def onControlModeSwitch(self, mode):
        if mode == AnalogDetection.GPIO_PROGRAM:
            self.dataShowingPushButton.setEnabled(False)
            self.graphicShowingPushButton.setEnabled(False)
            DevAttr.OperationMode = DevAttr.ProgramMode
            self.showWidgetInContentWidget(widget=self.devProgramWidget)
        elif mode == AnalogDetection.GPIO_SINGLE:
            self.dataShowingPushButton.setEnabled(True)
            self.graphicShowingPushButton.setEnabled(True)
            self.onDataShowingPushButtonClicked()

    def onOrganizedPlayPushButtonClicked(self):
        try:
            organizedPlay = OrganizedPlay()
            organizedPlay.playsActive.connect(self.devProgramWidget.onAutoRunning)
            print("organizedPlay exit code:", organizedPlay.exec_())
        except Exception as e:
            print("create organized play error", str(e))
    def showWidgetInContentWidget(self, index = 0, widget = None):
        for w in self.contentWidgetList:
            w.hide()
        if widget is None:
            if len(self.contentWidgetList) != 0:
                self.contentWidgetList[0].show()
        else:
            widget.show()

    def onDatabaseState(self, s):
        if s:
            self.databaseLabel.setText("数据库忙")
        else:
            self.databaseLabel.setText("数据库闲")
    def onSystemManagementPushButtonClicked(self):
        login = AccountLogin()
        if login.exec_():
            try:
                sysManagement = SystemManagement()
                sysManagement.somthingChanged.connect(self.onSysManagementSomthingChanged)
                sysManagement.exec_()
            except Exception as e:
                print(str(e))
    def onNetFramePushButtonClicked(self):
        try:
            deviceNetGraphic = DeviceNetGraphic(self.getAllDevice())
            for dev in self.getAllDevice():
                deviceNetGraphic.stateChanged(dev, False, True)
            deviceNetGraphic.exec_()
        except Exception as e:
            print(str(e))

    @pyqtSlot(str, str)
    def onSysManagementSomthingChanged(self, name, value):
        self.plcSocketManagement.emit(1)

    @pyqtSlot(int, dict)
    def onTcpServerUpdateSetting(self, sec, setting):
        try:
            id = setting["DevId"]
            targetPos =  setting["targetPos"]
            UpLimited = setting["UpLimited"]
            DownLimited = setting["DownLimited"]
            for dev in DevAttr.devAttrList:
                if dev.devId == id:
                    dev.targetPos = targetPos
                    dev.upLimitedPos = UpLimited
                    dev.downLimitedPos = DownLimited
                    if dev.targetPos > 100:
                        dev.setStateWord(DevAttr.SW_LowerLimit)
                    else:
                        dev.clearStateWord(DevAttr.SW_LowerLimit)
                    dev.valueChanged.emit(dev.devId, dev.devName)
                    self.savingParaSetting.emit(dev.devName, targetPos, UpLimited, DownLimited)
        except Exception as e:
            print("On Tcp Server update Setting", str(e))

    @pyqtSlot(int, dict)
    def onTcpServerOperationalCtrl(self, sec, content):
        DevAttr.singleCtrlOperation[sec] = content["State"]

    @pyqtSlot(int, dict)
    def onTcpServerSpeedSet(self, sec, content):
        DevAttr.singleCtrlSpeed[sec] = content["Value"]

    def getVersion(self):
        return "Version {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])

    @pyqtSlot(dict)
    def onTcpServerGetDevConnectingInfo(self, info):
        devIsConnecting = False
        if isinstance(info, dict):
            for name, id in info.items():
                if name is not None:
                    devIsConnecting = True
                    break
        if devIsConnecting:
            self.internetLabel.setText(self.tr("设备已连接"))
        else:
            self.internetLabel.setText(self.tr("无设备连接"))

    def closeEvent(self, *args, **kwargs):
        login = AccountLogin()
        if login.exec_():
            args[0].accept()
        else:
            args[0].ignore()

    def onPhysicalGPIOState(self, gpio, state):
        if state == AnalogDetection.KEY_DOWN:
            focusWidget = QApplication.focusWidget()
            if focusWidget is None: return
            if gpio == AnalogDetection.GPIO_TURN_NEXT:
                tabKey = QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.NoModifier, "right")
                QApplication.sendEvent(focusWidget, tabKey)
            elif  gpio == AnalogDetection.GPIO_TURN_PREV:
                tabKey = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier, "left")
                QApplication.sendEvent(focusWidget, tabKey)
            elif gpio == AnalogDetection.GPIO_RUN:
                tabKey = QKeyEvent(QEvent.KeyPress, Qt.Key_F5, Qt.NoModifier, "f5")
                QApplication.sendEvent(focusWidget, tabKey)
            elif gpio == AnalogDetection.GPIO_STOP:
                tabKey = QKeyEvent(QEvent.KeyPress, Qt.Key_F6, Qt.NoModifier, "f6")
                QApplication.sendEvent(focusWidget, tabKey)
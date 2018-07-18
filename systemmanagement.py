#!/usr/bin/env python
# -*- coding:utf8 -*-

from PyQt5.QtWidgets import *
from  PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from ui import ui_systemmanagementwidget
from config import *
import  os
import  time
import  base64
import  collections

class AccountLogin(QDialog):
    accountState = pyqtSignal(bool)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.accountNameLabel = QLabel("用户名：")
        self.accountNameLineEdit = QLineEdit("Administrator")
        self.accountNameLabel.setBuddy(self.accountNameLineEdit)
        self.nameHLayout = QHBoxLayout()
        self.nameHLayout.addWidget(self.accountNameLabel)
        self.nameHLayout.addWidget(self.accountNameLineEdit)

        self.accountPasswdLabel = QLabel("密码:")
        self.accountPasswdLineEdit = QLineEdit()
        self.accountPasswdLineEdit.setEchoMode(QLineEdit.Password)
        self.accountPasswdLabel.setBuddy(self.accountNameLineEdit)
        self.accountHLayout = QHBoxLayout()
        self.accountHLayout.addWidget(self.accountPasswdLabel)
        self.accountHLayout.addWidget(self.accountPasswdLineEdit)

        self.dialogButtonBox  = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.nameHLayout)
        self.mainLayout.addLayout(self.accountHLayout)
        self.mainLayout.addWidget(self.dialogButtonBox)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("请输入用户名和密码")
        self.dialogButtonBox.button(QDialogButtonBox.Ok).clicked.connect(self.userEntry)
        self.dialogButtonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.accountPasswdLineEdit.setFocus()
        # Fixme for test code
        try:
            self.accountPasswdLineEdit.setText(Config.cryptoValue("Password"))
            self.dialogButtonBox.button(QDialogButtonBox.Ok).animateClick()
        except Exception as e:
            print(str(e))
    def userEntry(self):
        password = self.accountPasswdLineEdit.text()
        p = str(base64.decodestring(bytes(Config.value("Password"), encoding="utf-8")), encoding="utf-8")
        print("user input", password)
        if password == p:
            self.accept()
        else:
            QMessageBox.warning(self, "Warning", "Password error, please try again!")

class SystemManagement(QDialog, ui_systemmanagementwidget.Ui_SystemManagementWidget):
    somthingChanged = pyqtSignal(str, str)
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("系统管理"))
        # regExp = QRegExp(r"((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)")
        # self.serverIpLineEdit.setValidator(QRegExpValidator(regExp))
        # self.serverIpLineEdit.setText(Config.value("ServerIp"))
        # self.serverIpLineEdit.editingFinished.connect(self.onServerIpLineEditingEditFinished)
        self.setFixedSize(self.sizeHint())
        self.networkInfo = self.getAllNetworkInterfaces()
        self.networkNameComboBox.addItems(self.networkInfo.keys())
        self.networkNameComboBox.currentTextChanged.connect(self.onNetworkNameComboBoxCurrentTextChanged)
        self.networkNameComboBox.setCurrentIndex(1)
        fm = QFontMetricsF(self.font())
        rect = fm.boundingRect("yyyy-MM-dd  hh:mm:ss")
        self.timeLineEdit.setMinimumWidth(rect.width())
        reg = QRegExp("""((([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|
                        [1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|
                        ((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|
                        ((([0-9]{2})(0[48]|[2468][048]|[13579][26])|
                        ((0[48]|[2468][048]|[3579][26])00))-02-29))\s([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$""")
        self.timeLineEdit.setValidator(QRegExpValidator(reg))
        self.timeLineEdit.returnPressed.connect(self.onTimeLineReturnPressed)
        self.timeLineEdit.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
        try:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.onTimerTimeout)
            self.timer.start(1000)
        except Exception as e:
            print(str(e))
    def onServerIpLineEditingEditFinished(self):
        pass
    def getAllNetworkInterfaces(self):
        ifaceList = QNetworkInterface.allInterfaces()
        networkInfo = collections.OrderedDict()
        for face in ifaceList:
            networkInfo[face.humanReadableName()] = []
            entryList = face.addressEntries()
            for entry in entryList:
                if entry.ip().protocol() == QAbstractSocket.IPv4Protocol:
                    networkInfo[face.humanReadableName()].append(entry.ip().toString())
                    networkInfo[face.humanReadableName()].append(entry.netmask().toString())
        return networkInfo
    def onNetworkNameComboBoxCurrentTextChanged(self, text):
        self.ipLineEdit.setText(self.networkInfo[text][0])
        self.netmaskLineEdit.setText(self.networkInfo[text][1])
    def onTimerTimeout(self):
        if not self.timeLineEdit.isModified():
            self.timeLineEdit.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss"))
    def onTimeLineReturnPressed(self):
        self.timeLineEdit.setModified(False)
        (date, time) = self.timeLineEdit.text().split(" ")
        print("Todo: update system time", os.system('date {}'.format(date)))
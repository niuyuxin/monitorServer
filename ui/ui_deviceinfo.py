# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'deviceinfo.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DeviceInfo(object):
    def setupUi(self, DeviceInfo):
        DeviceInfo.setObjectName("DeviceInfo")
        DeviceInfo.resize(193, 82)
        self.gridLayout = QtWidgets.QGridLayout(DeviceInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(DeviceInfo)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(DeviceInfo)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 1)
        self.devNameLabel = QtWidgets.QLabel(DeviceInfo)
        self.devNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.devNameLabel.setObjectName("devNameLabel")
        self.gridLayout.addWidget(self.devNameLabel, 0, 1, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(DeviceInfo)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(DeviceInfo)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.retranslateUi(DeviceInfo)
        QtCore.QMetaObject.connectSlotsByName(DeviceInfo)

    def retranslateUi(self, DeviceInfo):
        _translate = QtCore.QCoreApplication.translate
        DeviceInfo.setWindowTitle(_translate("DeviceInfo", "Form"))
        self.label_2.setText(_translate("DeviceInfo", "速度："))
        self.devNameLabel.setText(_translate("DeviceInfo", "设备名称"))
        self.label_3.setText(_translate("DeviceInfo", "位置："))


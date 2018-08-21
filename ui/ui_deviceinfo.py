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
        DeviceInfo.resize(208, 250)
        self.gridLayout = QtWidgets.QGridLayout(DeviceInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.programDevNameLabel = QtWidgets.QLabel(DeviceInfo)
        self.programDevNameLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.programDevNameLabel.setObjectName("programDevNameLabel")
        self.gridLayout.addWidget(self.programDevNameLabel, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(DeviceInfo)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.speedLineEdit = QtWidgets.QLineEdit(DeviceInfo)
        self.speedLineEdit.setEnabled(False)
        self.speedLineEdit.setObjectName("speedLineEdit")
        self.gridLayout.addWidget(self.speedLineEdit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(DeviceInfo)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.posLineEdit = QtWidgets.QLineEdit(DeviceInfo)
        self.posLineEdit.setEnabled(False)
        self.posLineEdit.setObjectName("posLineEdit")
        self.gridLayout.addWidget(self.posLineEdit, 2, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(DeviceInfo)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.directionLineEdit = QtWidgets.QLineEdit(DeviceInfo)
        self.directionLineEdit.setEnabled(False)
        self.directionLineEdit.setObjectName("directionLineEdit")
        self.gridLayout.addWidget(self.directionLineEdit, 3, 1, 1, 1)
        self.devPicLabel = QtWidgets.QLabel(DeviceInfo)
        self.devPicLabel.setMinimumSize(QtCore.QSize(190, 80))
        self.devPicLabel.setText("")
        self.devPicLabel.setObjectName("devPicLabel")
        self.gridLayout.addWidget(self.devPicLabel, 4, 0, 1, 2)
        self.inverterPicLabel = QtWidgets.QLabel(DeviceInfo)
        self.inverterPicLabel.setText("")
        self.inverterPicLabel.setObjectName("inverterPicLabel")
        self.gridLayout.addWidget(self.inverterPicLabel, 0, 0, 1, 1)

        self.retranslateUi(DeviceInfo)
        QtCore.QMetaObject.connectSlotsByName(DeviceInfo)

    def retranslateUi(self, DeviceInfo):
        _translate = QtCore.QCoreApplication.translate
        DeviceInfo.setWindowTitle(_translate("DeviceInfo", "Form"))
        self.programDevNameLabel.setText(_translate("DeviceInfo", "设备名称"))
        self.label_2.setText(_translate("DeviceInfo", "速度："))
        self.label_3.setText(_translate("DeviceInfo", "位置："))
        self.label_5.setText(_translate("DeviceInfo", "方向："))


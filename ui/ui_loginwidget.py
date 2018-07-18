# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loginwidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_loginWidget(object):
    def setupUi(self, loginWidget):
        loginWidget.setObjectName("loginWidget")
        loginWidget.resize(242, 169)
        self.verticalLayout = QtWidgets.QVBoxLayout(loginWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(loginWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.frame = QtWidgets.QFrame(loginWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.loginPushButton = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loginPushButton.sizePolicy().hasHeightForWidth())
        self.loginPushButton.setSizePolicy(sizePolicy)
        self.loginPushButton.setObjectName("loginPushButton")
        self.gridLayout.addWidget(self.loginPushButton, 4, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.newUerPushButton = QtWidgets.QPushButton(self.frame)
        self.newUerPushButton.setObjectName("newUerPushButton")
        self.gridLayout.addWidget(self.newUerPushButton, 4, 2, 1, 1)
        self.passwordLineEdit = QtWidgets.QLineEdit(self.frame)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.gridLayout.addWidget(self.passwordLineEdit, 3, 0, 1, 3)
        self.accountLineEdit = QtWidgets.QLineEdit(self.frame)
        self.accountLineEdit.setObjectName("accountLineEdit")
        self.gridLayout.addWidget(self.accountLineEdit, 1, 0, 1, 3)
        self.verticalLayout.addWidget(self.frame)

        self.retranslateUi(loginWidget)
        QtCore.QMetaObject.connectSlotsByName(loginWidget)
        loginWidget.setTabOrder(self.accountLineEdit, self.passwordLineEdit)
        loginWidget.setTabOrder(self.passwordLineEdit, self.loginPushButton)

    def retranslateUi(self, loginWidget):
        _translate = QtCore.QCoreApplication.translate
        loginWidget.setWindowTitle(_translate("loginWidget", "Form"))
        self.label.setText(_translate("loginWidget", "用户登陆系统"))
        self.label_2.setText(_translate("loginWidget", "账号："))
        self.loginPushButton.setText(_translate("loginWidget", "登陆"))
        self.label_3.setText(_translate("loginWidget", "密码："))
        self.newUerPushButton.setText(_translate("loginWidget", "新建用户"))


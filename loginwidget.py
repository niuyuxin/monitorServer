#!/usr/bin/env python3


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from ui import ui_loginwidget
from config import Config
from mainwindow import MainWindow

class LoginWidget(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.loginWidget = QWidget(self)
        self.loginDialog = ui_loginwidget.Ui_loginWidget()
        self.loginDialog.setupUi(self.loginWidget)
        self.loginDialog.loginPushButton.clicked.connect(self.onLoginPushButtonClicked)
        self.showFullScreen()

        # Fixme: Auto login, for testing...
        self.loginDialog.accountLineEdit.setText("root")
        self.loginDialog.passwordLineEdit.setText(Config.cryptoValue("Password/root"))
        self.loginDialog.loginPushButton.setFocus()
        self.loginDialog.loginPushButton.animateClick()
    def paintEvent(self, *args, **kwargs):
        rect = self.geometry()
        x = int(rect.width() - self.loginWidget.width()*1.4) if rect.width() > self.loginWidget.width()*1.4 else 0
        y = int(rect.height() - self.loginWidget.height()*1.4) if rect.height() > self.loginWidget.height()*1.4 else 0
        self.loginWidget.move(x, y)
    def onLoginPushButtonClicked(self):
        inputInfo = (self.loginDialog.accountLineEdit.text(), self.loginDialog.passwordLineEdit.text())
        print(inputInfo)
        userList = Config.getGroupKeys("Account")
        for user in userList:
            name = Config.value("Account/{}".format(user))
            if name == inputInfo[0]:
                p = Config.cryptoValue("Password/{}".format(name))
                if p == inputInfo[1]:
                    self.accept()
                    return
                return

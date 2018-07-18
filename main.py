#!/usr/bin/env python

import  sys
import  os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from mainwindow import MainWindow
from config import Config
from loginwidget import LoginWidget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("touchscreenserver.qss", 'r') as qssFile:
            styleSheet = qssFile.readlines()
        qApp.setStyleSheet("".join(styleSheet))
    except Exception as e:
        print(str(e))
        QMessageBox.warning(None,
                            "Warning",
                            "Maybe you lost style sheet file for this Application",
                            QMessageBox.Ok)
    Config()
    ret = LoginWidget().exec_()
    if ret:
        mainWindow = MainWindow()
        mainWindow.setWindowTitle("MonitorServer")
        mainWindow.show()
        # mainWindow.setEnabled(False)
        sys.exit(app.exec_())
    else:
        sys.exit(app.exit(0))


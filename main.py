#!/usr/bin/env python

import  sys
import  os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from mainwindow import MainWindow


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
    mainWindow = MainWindow()
    mainWindow.setWindowTitle("MonitorServer")
    mainWindow.show()

    app.exec_()


#!/usr/bin/env python

import  sys
from PyQt5.QtWidgets import *
from mainwindow import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()


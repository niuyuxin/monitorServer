#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import  ui_organizedplaydialog
from config import  *
from rcc import rc_touchscreenresource

class NewAction(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("新建剧目")
class EditingAction(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("编辑剧目")

class ListWidget(QListWidget):
    deletedAction = pyqtSignal()
    modifiedAction = pyqtSignal()
    activedAction = pyqtSignal()
    addedAction = pyqtSignal()
    renamedAction = pyqtSignal()
    def __init__(self, parent = None):
        super().__init__(parent)
    def contextMenuEvent(self, *args, **kwargs):
        menu = QMenu(self)
        if isinstance(self.itemAt(self.mapFromGlobal(QCursor.pos())), QListWidgetItem):
            action = QAction(self.tr("删除"), self)
            action.triggered.connect(self.deletedAction)
            menu.addAction(action)
            action = QAction(self.tr("修改"), self)
            action.triggered.connect(self.modifiedAction)
            menu.addAction(action)
            action = QAction(self.tr("激活"), self)
            action.triggered.connect(self.activedAction)
            menu.addAction(action)
            action = QAction(self.tr("重命名"), self)
            action.triggered.connect(self.renamedAction)
            menu.addAction(action)
        else:
            action = QAction(self.tr("新建"), self)
            action.triggered.connect(self.addedAction)
            menu.addAction(action)
        menu.exec_(QCursor.pos())
class OrganizedPlay(QDialog, ui_organizedplaydialog.Ui_organizedPlayDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.returnPushButton.setDefault(True)
        # add plays
        self.contentLayout = QHBoxLayout()
        self.contentListWidget = ListWidget()
        self.contentLayout.addWidget(self.contentListWidget)
        self.contentListWidget.setViewMode(QListView.IconMode)
        self.contentListWidget.setSpacing(20)
        self.contentListWidget.setResizeMode(QListView.Adjust)
        self.contentListWidget.setMovement(QListView.Static)
        for i in range(400):
            icon = QIcon(":/images/images/dirpic.jpg")
            item = QListWidgetItem()
            item.setText("testFile{}".format(i))
            item.setIcon(icon)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.contentListWidget.addItem(item)
        self.contentFrame.setLayout(self.contentLayout)
        # push button clicked and slots
        self.editingPushButton.clicked.connect(self.onEditingPushButtonClicked)
        self.newPushButton.clicked.connect(self.onNewPushButtonClicked)
        self.renamePushButton.clicked.connect(self.onRenamePushButtonClicked)
        self.deletePushButton.clicked.connect(self.onDeletePushButtonClicked)
        self.exportPushButton.clicked.connect(self.onExportPushButtonClicked)
        self.activePushButton.clicked.connect(self.onActivePushButtonClicked)
        # content list widget signals and slots
        self.contentListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.contentListWidget.itemDoubleClicked.connect(self.onContentListWidgetItemDoubleClicked)
        self.contentListWidget.deletedAction.connect(self.onDeletePushButtonClicked)
        self.contentListWidget.activedAction.connect(self.onActivePushButtonClicked)
        self.contentListWidget.modifiedAction.connect(self.onEditingPushButtonClicked)
        self.contentListWidget.renamedAction.connect(self.onRenamePushButtonClicked)
        self.contentListWidget.addedAction.connect(self.onNewPushButtonClicked)
    def onEditingPushButtonClicked(self):
        e = EditingAction()
        e.exec_()
    def onContentListWidgetItemDoubleClicked(self, widget): pass
        # widget.setFlags(widget.flags() | Qt.ItemIsEditable)

    def onNewPushButtonClicked(self):
        new = NewAction()
        new.exec_()
    def onRenamePushButtonClicked(self):
        widget = self.contentListWidget.currentItem()
        if widget is not None:
            self.contentListWidget.editItem(widget)
    def onDeletePushButtonClicked(self):
        self.tipsLabel.setText(getFunctionName())
    def onExportPushButtonClicked(self):
        self.tipsLabel.setText(getFunctionName())
    def onActivePushButtonClicked(self):
        self.tipsLabel.setText(getFunctionName())


#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import ui_organizedplaydialog
from config import *
from rcc import rc_touchscreenresource
from ui import ui_editingdevicedialog

class ListWidgetItem(QListWidgetItem):
    def __init__(self, sceneOfDevice = {}, name = "", QIcon = QIcon(), parent=None):
        super().__init__(parent)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setText(name)
        self.setIcon(QIcon)
        self.sceneOfDevice = sceneOfDevice
        self.sceneQuantity = len(self.sceneOfDevice)

class ListWidget(QListWidget):
    deletedAction = pyqtSignal()
    editingAction = pyqtSignal()
    activedAction = pyqtSignal()
    addedAction = pyqtSignal()
    renamedAction = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListView.IconMode)
        self.setSpacing(20)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)

    def contextMenuEvent(self, *args, **kwargs):
        menu = QMenu(self)
        if isinstance(self.itemAt(self.mapFromGlobal(QCursor.pos())), ListWidgetItem):
            action = QAction(self.tr("删除"), self)
            action.triggered.connect(self.deletedAction)
            menu.addAction(action)
            action = QAction(self.tr("编辑"), self)
            action.triggered.connect(self.editingAction)
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

class NewAction(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建剧目")
        self.nameLabel = QLabel(self.tr("请输入剧目名称:"))
        self.nameLineEdit = QLineEdit()
        self.sceneQuantityLabel = QLabel(self.tr("总场次:"))
        self.sceneQuantitySpinBox = QSpinBox()
        self.sceneQuantitySpinBox.setMaximum(50)
        self.accessPushButton = QPushButton("Yes")
        self.rejectPushButton = QPushButton("Cancel")
        self.rejectPushButton.setDefault(True)
        self.accessPushButton.clicked.connect(self.accept)
        self.rejectPushButton.clicked.connect(self.reject)
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.nameLabel, 0, 0)
        self.gridLayout.addWidget(self.nameLineEdit, 0, 1)
        self.gridLayout.addWidget(self.sceneQuantityLabel, 1, 0)
        self.gridLayout.addWidget(self.sceneQuantitySpinBox, 1, 1)
        self.gridLayout.addWidget(self.accessPushButton, 2, 0)
        self.gridLayout.addWidget(self.rejectPushButton, 2, 1)
        self.setLayout(self.gridLayout)
    def accept(self):
        if not self.sceneQuantitySpinBox.value() or not self.nameLineEdit.text():
            QMessageBox.warning(self, "Error",
                                self.tr("请填写正确的内容"), QMessageBox.Ok)
        else:
            self.done(1)
class EditingDevAction(QDialog, ui_editingdevicedialog.Ui_EditingDevDialog):
    def __init__(self, subDevDict=None, scene=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("编辑设备"))
        self.optionListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        try:
            for key in subDevDict:
                for value in subDevDict[key]:
                    item = ListWidgetItem(name=value, QIcon=QIcon(":/images/images/opendirpic.jpg"))
                    self.optionListWidget.addItem(item)
        except Exception as e:
            print(str(e))

class EditingSceneAction(QDialog):
    def __init__(self, subDevDict=None, scene = None, parent=None):
        super().__init__(parent)
        self.subDevDict = subDevDict
        self.setWindowTitle("编辑场次")
        self.sceneLayout = QVBoxLayout()
        self.tipLabel = QLabel(self.tr("请选择要编辑场次，并点击确认按键"))
        self.confirmPushButton = QPushButton(self.tr("确认"))
        self.confirmPushButton.clicked.connect(self.onConfirmPushButtonClicked)
        self.deletePushButton = QPushButton(self.tr("删除"))
        self.newPushButton = QPushButton(self.tr("新建"))
        self.cancelPushButton = QPushButton(self.tr("取消"))
        self.cancelPushButton.setDefault(True)
        self.cancelPushButton.clicked.connect(self.reject)
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.confirmPushButton)
        self.buttonLayout.addWidget(self.cancelPushButton)
        self.buttonLayout.addWidget(self.deletePushButton)
        self.buttonLayout.addWidget(self.newPushButton)
        self.sceneListWidget = QListWidget(self)
        self.sceneListWidget.setViewMode(QListView.IconMode)
        self.sceneListWidget.setSpacing(20)
        self.sceneListWidget.setResizeMode(QListView.Adjust)
        self.sceneListWidget.setMovement(QListView.Static)
        self.sceneLayout.addWidget(self.tipLabel)
        self.sceneLayout.addWidget(self.sceneListWidget)
        self.sceneLayout.addLayout(self.buttonLayout)
        self.setLayout(self.sceneLayout)
        try:
            for sceneItem in scene.items():
                item = ListWidgetItem(sceneOfDevice=sceneItem,
                                      name="File{}".format(sceneItem[0]),
                                      QIcon=QIcon(":/images/images/dirpic.jpg"))
                self.sceneListWidget.addItem(item)
        except Exception as e:
            print(str(e))
    def onConfirmPushButtonClicked(self):
        dev = EditingDevAction(subDevDict=self.subDevDict)
        dev.exec_()

class OrganizedPlay(QDialog, ui_organizedplaydialog.Ui_organizedPlayDialog):
    def __init__(self, subDevDict=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.subDevDict = subDevDict
        self.returnPushButton.setDefault(True)
        # add plays
        self.contentLayout = QHBoxLayout()
        self.contentListWidget = ListWidget()
        self.contentLayout.addWidget(self.contentListWidget)
        for i in range(15):
            icon = QIcon(":/images/images/dirpic.jpg")
            di = {1:["dev1","dev2","dev3"], 2:["dev3", "dev4", "dev5"], 3:["dev6", "dev7", "dev8"]}
            item = ListWidgetItem(sceneOfDevice=di, name="File{}".format(i), QIcon=icon)
            self.contentListWidget.addItem(item)
        self.contentFrame.setLayout(self.contentLayout)
        # push button clicked and slots
        self.editingPushButton.clicked.connect(self.onEditingPushButtonClicked)
        self.newPushButton.clicked.connect(self.onNewPushButtonClicked)
        self.renamePushButton.clicked.connect(self.onRenamePushButtonClicked)
        self.deletePushButton.clicked.connect(self.onDeletePushButtonClicked)
        self.exportPushButton.clicked.connect(self.onExportPushButtonClicked)
        self.activePushButton.clicked.connect(self.onActivePushButtonClicked)
        # contentlistwidget signals and slots
        self.contentListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.contentListWidget.itemDoubleClicked.connect(self.onContentListWidgetItemDoubleClicked)
        self.contentListWidget.deletedAction.connect(self.onDeletePushButtonClicked)
        self.contentListWidget.activedAction.connect(self.onActivePushButtonClicked)
        self.contentListWidget.editingAction.connect(self.onEditingPushButtonClicked)
        self.contentListWidget.renamedAction.connect(self.onRenamePushButtonClicked)
        self.contentListWidget.addedAction.connect(self.onNewPushButtonClicked)
        self.contentListWidget.itemChanged.connect(self.onListWidgetItemChanged)
    def onListWidgetItemChanged(self, widget):
        print(widget.text())

    def onEditingPushButtonClicked(self):
        widget = self.contentListWidget.currentItem()
        if widget is None:
            QMessageBox.warning(self,
                                "Warning",
                                self.tr("请选中要编辑的剧目"),
                                QMessageBox.Ok | QMessageBox.Cancel)
        else:
            print(widget.sceneOfDevice) # how many plays...
            e = EditingSceneAction(subDevDict=self.subDevDict, scene=widget.sceneOfDevice)
            e.resize(500, 300)
            e.exec_()

    def onContentListWidgetItemDoubleClicked(self, widget):
        self.onEditingPushButtonClicked()

    def onNewPushButtonClicked(self):
        widget = self.contentListWidget.currentItem()# cancel selected.
        if widget:
            widget.setSelected(False)
        new = NewAction()
        if new.exec_():
            item = ListWidgetItem(name=new.nameLineEdit.text(),
                                  QIcon=QIcon(":/images/images/dirpic.jpg"))
            self.contentListWidget.addItem(item)
        else:
            print("rejected")


    def onRenamePushButtonClicked(self):
        widget = self.contentListWidget.currentItem()
        if widget is not None:
            self.contentListWidget.editItem(widget)

    def onDeletePushButtonClicked(self):
        currentWidget = self.contentListWidget.currentItem()
        if not currentWidget:
            QMessageBox.warning(self, self.tr("删除操作"),
                            self.tr("请选中要删除的剧目！"), QMessageBox.Ok | QMessageBox.Cancel)
        else:
            ret = QMessageBox.warning(self, self.tr("删除操作"),
                            self.tr("确认要删除当前剧目吗？"), QMessageBox.Ok | QMessageBox.Cancel)
            if ret == QMessageBox.Ok:
                row = self.contentListWidget.row(currentWidget)
                self.contentListWidget.takeItem(row)
                del currentWidget


    def onExportPushButtonClicked(self):
        self.tipsLabel.setText(getFunctionName())

    def onActivePushButtonClicked(self):
        self.tipsLabel.setText(getFunctionName())
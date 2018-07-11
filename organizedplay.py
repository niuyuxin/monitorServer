#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from ui import ui_organizedplaydialog
from config import *
from rcc import rc_touchscreenresource
from ui import ui_editingdevicedialog

class PlaysListWidgetItem(QListWidgetItem):
    def __init__(self, scenes, playName, QIcon, parent=None):
        super().__init__(parent)
        self.setFlags(self.flags()|Qt.ItemIsEditable)
        self.setText(playName)
        self.setIcon(QIcon)
        self.scenes = scenes

class SceneListWidgetItem(QListWidgetItem):
    def __init__(self, devices, sceneName, QIcon, parent=None):
        super().__init__(parent)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setText(sceneName)
        self.setIcon(QIcon)
        self.devices = devices

class DeviceListWidgetItem(QListWidgetItem):
    def __init__(self, deviceName, speed=0, targetPos=0, QIcon=None, parent=None):
        super().__init__(parent)
        self.setText(deviceName)
        self.setIcon(QIcon)
        self.speed = speed
        self.targetPos = targetPos

class ListWidget(QListWidget):
    deletedAction = pyqtSignal()
    editingAction = pyqtSignal()
    activedAction = pyqtSignal()
    addedAction = pyqtSignal()
    renamedAction = pyqtSignal()

    def __init__(self, active=True, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.active = active
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setSpacing(20)

    def contextMenuEvent(self, *args, **kwargs):
        menu = QMenu(self)
        if isinstance(self.itemAt(self.mapFromGlobal(QCursor.pos())), QListWidgetItem):
            action = QAction(self.tr("编辑"), self)
            action.triggered.connect(self.editingAction)
            menu.addAction(action)
            if self.active:
                action = QAction(self.tr("激活"), self)
                action.triggered.connect(self.activedAction)
                menu.addAction(action)
            action = QAction(self.tr("重命名"), self)
            action.triggered.connect(self.renamedAction)
            menu.addAction(action)
            action = QAction(self.tr("删除"), self)
            action.triggered.connect(self.deletedAction)
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
    def __init__(self, subDevDict=None, devices=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("编辑设备"))
        self.optionListWidget.setResizeMode(QListWidget.Adjust)
        self.optionListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.selectedListWidget.itemClicked.connect(self.onSelectedListWidgetItemClicked)
        self.rmPushButton.clicked.connect(self.onRmPushButtonClicked)
        self.addPushButton.clicked.connect(self.onAddPushButtonClicked)
        for key in subDevDict:
            for value in subDevDict[key]:
                item = DeviceListWidgetItem(deviceName=value, QIcon=QIcon(":/images/images/dirpic.jpg"))
                self.optionListWidget.addItem(item)
        for dev in devices:
            item = DeviceListWidgetItem(deviceName=dev, QIcon=QIcon(":/images/images/opendirpic.jpg"))
            self.selectedListWidget.addItem(item)
    def onRmPushButtonClicked(self):
        row = self.selectedListWidget.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", self.tr("请选择要删除的设备，再点击 '>>>'"), QMessageBox.Ok)
        else:
            w = self.selectedListWidget.takeItem(row)
            del w

    def onAddPushButtonClicked(self):
        row = self.optionListWidget.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Warning", self.tr("请选择要添加的设备，再点击 '<<<'"), QMessageBox.Ok)
        else:
            w = self.optionListWidget.currentItem()
            item = DeviceListWidgetItem(deviceName=w.text(), QIcon=QIcon(":/images/images/opendirpic.jpg"))
            self.selectedListWidget.addItem(item)
    def onSelectedListWidgetItemClicked(self, w):
        self.posSpinBox.setValue(w.targetPos)
        self.speedSpinBox.setValue(w.speed)

class EditingSceneAction(QDialog):
    def __init__(self, subDevDict, scenes, parent=None):
        super().__init__(parent)
        self.subDevDict = subDevDict
        self.setWindowTitle("编辑场次")
        self.tipLabel = QLabel(self.tr("请选择要编辑场次，并点击确认按键"))
        # push button and slots
        self.editingPushButton = QPushButton(self.tr("编辑场次"))
        self.renamePushButton = QPushButton(self.tr("重命名场次"))
        self.newPushButton = QPushButton(self.tr("新建场次"))
        self.deletePushButton = QPushButton(self.tr("删除场次"))
        self.cancelPushButton = QPushButton(self.tr("取消"))
        self.cancelPushButton.clicked.connect(self.reject)
        self.editingPushButton.clicked.connect(self.onEditingPushButtonClicked)
        self.renamePushButton.clicked.connect(self.onRenamePushButtonClicked)
        self.newPushButton.clicked.connect(self.onNewPushButtonClicked)
        self.deletePushButton.clicked.connect(self.onDeletePushButtonClicked)
        # layout
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.editingPushButton)
        self.buttonLayout.addWidget(self.renamePushButton)
        self.buttonLayout.addWidget(self.newPushButton)
        self.buttonLayout.addWidget(self.deletePushButton)
        self.buttonLayout.addWidget(self.cancelPushButton)
        self.cancelPushButton.setDefault(True)
        # list Widget...
        self.sceneListWidget = ListWidget(active=False)
        self.sceneListWidget.itemDoubleClicked.connect(self.onEditingPushButtonClicked)
        self.sceneListWidget.editingAction.connect(self.onEditingPushButtonClicked)
        self.sceneListWidget.renamedAction.connect(self.onRenamePushButtonClicked)
        self.sceneListWidget.addedAction.connect(self.onNewPushButtonClicked)
        self.sceneListWidget.deletedAction.connect(self.onDeletePushButtonClicked)
        self.sceneListWidget.setFocusPolicy(Qt.ClickFocus)
        self.sceneListWidget.itemChanged.connect(self.onSceneListWidgetItemChanged)
        for sceneItem in scenes.items():
            item = SceneListWidgetItem(
                devices=sceneItem[1],
                sceneName="场次{}".format(sceneItem[0]),
                QIcon=QIcon(":/images/images/dirpic.jpg")
            )
            self.sceneListWidget.addItem(item)
        self.sceneListWidget.setEditTriggers(QListView.NoEditTriggers)
        self.sceneListWidget.setViewMode(QListView.IconMode)
        self.sceneListWidget.setSpacing(20)
        self.sceneListWidget.setResizeMode(QListView.Adjust)
        self.sceneListWidget.setMovement(QListView.Static)
        self.sceneLayout = QVBoxLayout()
        self.sceneLayout.addWidget(self.tipLabel)
        self.sceneLayout.addWidget(self.sceneListWidget)
        self.sceneLayout.addLayout(self.buttonLayout)
        self.setLayout(self.sceneLayout)
    def onSceneListWidgetItemChanged(self, widget):
        self.sceneListWidget.setSpacing(20)
        print(widget.text())
    def onEditingPushButtonClicked(self):
        sceneItem = self.sceneListWidget.currentItem()
        if sceneItem is None:
            QMessageBox.warning(self, "Warning", self.tr("请选择要编辑的场次！"), QMessageBox.Ok)
        else:
            dev = EditingDevAction(subDevDict=self.subDevDict, devices=sceneItem.devices)
            dev.exec_()
    def onRenamePushButtonClicked(self):
        widget = self.sceneListWidget.currentItem()
        if widget is not None:
            self.sceneListWidget.editItem(widget)
    def onNewPushButtonClicked(self):
        pass
    def onDeletePushButtonClicked(self):
        pass
class OrganizedPlay(QDialog, ui_organizedplaydialog.Ui_organizedPlayDialog):
    def __init__(self, subDevDict=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("编辑剧目"))
        self.subDevDict = subDevDict
        self.returnPushButton.setDefault(True)
        # add plays
        self.contentLayout = QVBoxLayout()
        self.contentListWidget = ListWidget()
        self.contentLayout.addWidget(self.contentListWidget)
        for i in range(200): # simulate reading data from database. create plays.
            icon = QIcon(":/images/images/dirpic.jpg")
            scenes={}
            count = 0
            for s in range(i+1):
                count += 1
                scenes[s] = [self.subDevDict["TouchScreen"][n] for n in range(0,100, count)]
            item = PlaysListWidgetItem(scenes=scenes, playName=self.tr("剧目")+"{}".format(i), QIcon=icon)
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
        self.contentListWidget.itemDoubleClicked.connect(self.onContentListWidgetItemDoubleClicked)
        self.contentListWidget.deletedAction.connect(self.onDeletePushButtonClicked)
        self.contentListWidget.activedAction.connect(self.onActivePushButtonClicked)
        self.contentListWidget.editingAction.connect(self.onEditingPushButtonClicked)
        self.contentListWidget.renamedAction.connect(self.onRenamePushButtonClicked)
        self.contentListWidget.addedAction.connect(self.onNewPushButtonClicked)
        self.contentListWidget.itemChanged.connect(self.onListWidgetItemChanged)
    def onListWidgetItemChanged(self, widget):
        self.contentListWidget.setSpacing(20)
        print(widget.text())

    def onEditingPushButtonClicked(self):
        playsItem = self.contentListWidget.currentItem()
        if playsItem is None:
            QMessageBox.warning(self,
                                "Warning", self.tr("请选中要编辑的剧目"), QMessageBox.Ok)
        else:
            editingScene = EditingSceneAction(subDevDict=self.subDevDict, scenes=playsItem.scenes)
            editingScene.resize(600, 300)
            editingScene.exec_()

    def onContentListWidgetItemDoubleClicked(self, widget):
        self.onEditingPushButtonClicked()

    def onNewPushButtonClicked(self):
        widget = self.contentListWidget.currentItem()# cancel selected.
        if widget:
            widget.setSelected(False)
        new = NewAction()
        if new.exec_():
            try:
                scenes = {}
                for s in range(new.sceneQuantitySpinBox.value()):
                    scenes[s]=[]
                item = PlaysListWidgetItem(scenes=scenes, playName=new.nameLineEdit.text(),
                                      QIcon=QIcon(":/images/images/dirpic.jpg"))
                self.contentListWidget.addItem(item)
            except Exception as e:
                print(str(e))
        else:
            print("rejected")


    def onRenamePushButtonClicked(self):
        widget = self.contentListWidget.currentItem()
        if widget is None:
            QMessageBox.warning(self,
                                self.tr("警告"), self.tr("请选中要重命名的剧目！"), QMessageBox.Ok)
        else:
            self.contentListWidget.editItem(widget)

    def onDeletePushButtonClicked(self):
        currentWidget = self.contentListWidget.currentItem()
        if not currentWidget:
            QMessageBox.warning(self, self.tr("删除操作"),
                            self.tr("请选中要删除的剧目！"), QMessageBox.Ok)
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
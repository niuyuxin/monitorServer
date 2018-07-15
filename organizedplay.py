#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import *
from ui import ui_organizedplaydialog
from config import *
from rcc import rc_touchscreenresource
from ui import ui_editingdevicedialog
from database import *
import random

class PlaysListWidgetItem(QListWidgetItem):
    def __init__(self, sId, playName, QIcon, parent=None):
        super().__init__(parent)
        self.setFlags(self.flags()|Qt.ItemIsEditable)
        self.selfId = sId
        self.setText(playName)
        self.setIcon(QIcon)

class SceneListWidgetItem(QListWidgetItem):
    def __init__(self, pId, sId, sceneName, QIcon, parent=None):
        super().__init__(parent)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setText(sceneName)
        self.setIcon(QIcon)
        self.parentId = pId
        self.selfId = sId

class DeviceListWidgetItem(QListWidgetItem):
    def __init__(self, pId, deviceName, sId="", speed=0, targetPos=0, QIcon=None, parent=None):
        super().__init__(parent)
        self.setText(deviceName)
        self.setIcon(QIcon)
        self.parentId = pId
        self.selfId = sId
        self.deviceIndex = deviceName
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
    def __init__(self, title="", tips="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.nameLabel = QLabel(self.tr(tips))
        self.nameLineEdit = QLineEdit()
        self.quantityLabel = QLabel(self.tr("数量:"))
        self.quantitySpinBox = QSpinBox()
        self.quantitySpinBox.setValue(1)
        self.quantitySpinBox.setMaximum(50)
        self.accessPushButton = QPushButton("Yes")
        self.rejectPushButton = QPushButton("Cancel")
        self.rejectPushButton.setDefault(True)
        self.accessPushButton.clicked.connect(self.accept)
        self.rejectPushButton.clicked.connect(self.reject)
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.nameLabel, 0, 0)
        self.gridLayout.addWidget(self.nameLineEdit, 0, 1)
        self.gridLayout.addWidget(self.quantityLabel, 1, 0)
        self.gridLayout.addWidget(self.quantitySpinBox, 1, 1)
        self.gridLayout.addWidget(self.accessPushButton, 2, 0)
        self.gridLayout.addWidget(self.rejectPushButton, 2, 1)
        self.setLayout(self.gridLayout)
    def accept(self):
        if not self.quantitySpinBox.value() or not self.nameLineEdit.text():
            QMessageBox.warning(self, "Error",
                                self.tr("请填写正确的内容"), QMessageBox.Ok)
        else:
            self.done(1)

class EditingDevAction(QDialog, ui_editingdevicedialog.Ui_EditingDevDialog):
    def __init__(self, pId, subDevDict=None, devices=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parentId = pId
        self.originList = []
        self.setWindowTitle(self.tr("编辑设备"))
        self.dataBase = QSqlDatabase.addDatabase("QSQLITE", "EditingDevActionConnection")
        self.dataBase.setDatabaseName(DataBase.dataBaseName)
        self.dataBase.setUserName("root")
        self.dataBase.setPassword("123456")
        if self.dataBase.open():pass
        else:
            print("dev action opened failure")
        self.optionListWidget.setResizeMode(QListWidget.Adjust)
        self.optionListWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.selectedListWidget.itemClicked.connect(self.onSelectedListWidgetItemClicked)
        self.rmPushButton.clicked.connect(self.onRmPushButtonClicked)
        self.addPushButton.clicked.connect(self.onAddPushButtonClicked)
        self.applyPushButton.clicked.connect(self.onApplyPushButtonClicked)
        self.cancelPushButton.clicked.connect(self.onCancelPushButtonClicked)
        for key in subDevDict:
            for value in subDevDict[key]:
                item = DeviceListWidgetItem(pId="", deviceName=value, QIcon=QIcon(":/images/images/dirpic.jpg"))
                self.optionListWidget.addItem(item)
        try:
            for dev in devices.items():
                self.originList.append(dev[0])
                item = DeviceListWidgetItem(sId=dev[0], pId=pId, deviceName=dev[1], QIcon=QIcon(":/images/images/opendirpic.jpg"))
                self.selectedListWidget.addItem(item)
        except Exception as e:
            print(str(e))
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
            id = QDateTime.currentDateTime().toString("yyyyMMddhhmmsszzz") + str(random.randint(0,100))
            item = DeviceListWidgetItem(sId=id, pId=self.parentId, deviceName=w.text(), QIcon=QIcon(":/images/images/opendirpic.jpg"))
            self.selectedListWidget.addItem(item)
    def onSelectedListWidgetItemClicked(self, w):
        self.posSpinBox.setValue(w.targetPos)
        self.speedSpinBox.setValue(w.speed)

    def onApplyPushButtonClicked(self):
        for row in range(self.selectedListWidget.count()):
            item = self.selectedListWidget.item(row)
            self.insertDev(item.selfId, item.parentId, item.deviceIndex)
            if item.selfId in self.originList:
                self.originList.remove(item.selfId)
        for item in self.originList:
            self.removeDev(item)
        self.accept()
    def onCancelPushButtonClicked(self):
        self.reject()
    def removeDev(self, selfIndex):
        try:
            sqlQuery = QSqlQuery(self.dataBase)
            if sqlQuery.exec_("""DELETE FROM DeviceSetInfo WHERE selfIndex = '{v}'""" \
                                      .format(v=selfIndex)):
                print("rm {} success".format(selfIndex))
            else:
                print("rm failure")
        except Exception as e:
            print(str(e))
    def insertDev(self, selfIndex, parentIndex, deviceIndex):
        sqlQuery = QSqlQuery(self.dataBase)
        if sqlQuery.exec_("""SELECT selfIndex FROM DeviceSetInfo WHERE selfIndex={}""".format(selfIndex)):
            if sqlQuery.next():
                    print("update scene success", selfIndex, deviceIndex)
                    return
            else:
                insertStr = "INSERT INTO DeviceSetInfo (selfIndex, parentIndex, deviceIndex) " \
                            "VALUES ('{s}', '{p}', '{d}')".format(s=selfIndex,p=parentIndex,d=deviceIndex)
                if sqlQuery.exec_(insertStr):
                    print("insert scene success", selfIndex, deviceIndex)
                else:
                    print("insert scene failure", selfIndex, deviceIndex)
class EditingSceneAction(QDialog):
    databaseConnectionName = "SceneConnection"
    def __init__(self, pId, subDevDict, scenes, parent=None):
        super().__init__(parent)
        self.subDevDict = subDevDict
        self.parentId = pId
        self.dataBase = QSqlDatabase.addDatabase("QSQLITE", EditingSceneAction.databaseConnectionName)
        self.dataBase.setDatabaseName(DataBase.dataBaseName)
        self.dataBase.setUserName("root")
        self.dataBase.setPassword("123456")
        if self.dataBase.open():pass
        else:
            print("scene opened failure")
        self.setWindowTitle("编辑场次")
        self.tipLabel = QLabel(self.tr("请选择要编辑场次，并点击确认按键"))
        # push button and slots
        self.editingPushButton = QPushButton(self.tr("编辑场次"))
        self.renamePushButton = QPushButton(self.tr("重命名场次"))
        self.newPushButton = QPushButton(self.tr("新建场次"))
        self.deletePushButton = QPushButton(self.tr("删除场次"))
        self.cancelPushButton = QPushButton(self.tr("返回"))
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
                pId=self.parentId,
                sId=sceneItem[0],
                sceneName="{}".format(sceneItem[1]),
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
        self.insertScene(name=widget.text(), id=widget.selfId, pId=widget.parentId)
    def onEditingPushButtonClicked(self):
        sceneItem = self.sceneListWidget.currentItem()
        if sceneItem is None:
            QMessageBox.warning(self, "Warning", self.tr("请选择要编辑的场次！"), QMessageBox.Ok)
        else:
            sqlQuery = QSqlQuery(self.dataBase)
            sqlQuery.exec_("""SELECT * FROM DeviceSetInfo WHERE parentIndex={}""".format(sceneItem.selfId))
            rec = sqlQuery.record()
            deviceIndexCol = rec.indexOf("deviceIndex")
            selfIndexCol = rec.indexOf("selfIndex")
            deviceDict = {}
            while sqlQuery.next():
                deviceDict[sqlQuery.value(selfIndexCol)] = sqlQuery.value(deviceIndexCol)
            dev = EditingDevAction(pId=sceneItem.selfId, subDevDict=self.subDevDict, devices=deviceDict)
            dev.exec_()
    def onRenamePushButtonClicked(self):
        widget = self.sceneListWidget.currentItem()
        if widget is not None:
            self.sceneListWidget.editItem(widget)
    def onNewPushButtonClicked(self):
        widget = self.sceneListWidget.currentItem()# cancel selected.
        if widget:
            widget.setSelected(False)
        new = NewAction(title="编辑场次",tips="场次名称：")
        if new.exec_():
            id = QDateTime.currentDateTime().toString("yyyyMMddhhmmsszzz") + str(random.randint(0,100))
            item = SceneListWidgetItem(
                pId=self.parentId,
                sId=id,
                sceneName=new.nameLineEdit.text(),
                QIcon=QIcon(":/images/images/dirpic.jpg")
            )
            self.sceneListWidget.addItem(item)
            self.insertScene(name=new.nameLineEdit.text(), id=id, pId=self.parentId)
    def onDeletePushButtonClicked(self):
        widget = self.sceneListWidget.currentItem()
        if not widget:
            QMessageBox.warning(self, self.tr("删除操作"),
                            self.tr("请选中要删除的场次！"), QMessageBox.Ok)
        else:
            ret = QMessageBox.warning(self, self.tr("删除操作"),
                            self.tr("确认要删除当前场次吗？"), QMessageBox.Ok | QMessageBox.Cancel)
            if ret == QMessageBox.Ok:
                sqlQuery = QSqlQuery(self.dataBase)
                ret = sqlQuery.exec_("""DELETE FROM DeviceSetInfo WHERE parentIndex = '{pId}'""" \
                                     .format(pId=widget.selfId))
                ret = sqlQuery.exec_("""DELETE FROM SceneInfo WHERE selfIndex = '{sId}'""" \
                                     .format(sId=widget.selfId))
                row = self.sceneListWidget.currentRow()
                self.sceneListWidget.takeItem(row)
    def insertScene(self, name, id, pId):
        sqlQuery = QSqlQuery(self.dataBase)
        if sqlQuery.exec_("""SELECT selfIndex FROM SceneInfo"""):
            while sqlQuery.next():
                if sqlQuery.value(0) == id:
                    ret = sqlQuery.exec_("UPDATE SceneInfo SET sceneName='{n}' where selfIndex='{index}'"
                                   .format(n=name, index=id))
                    print("update scene success", name, id)
                    return
            else:
                insertStr = "INSERT INTO SceneInfo (sceneName, selfIndex, parentIndex) " \
                            "VALUES ('{name}', '{id}', '{pId}')".format(name=name,id=id,pId=pId)
                print(insertStr)
                if sqlQuery.exec_(insertStr):
                    print("insert scene success", name, id)
                else:
                    print("insert scene failure", name, id)
class OrganizedPlay(QDialog, ui_organizedplaydialog.Ui_organizedPlayDialog):
    sqlDatabaseConntionName = "organizedPlayConnection"
    insertPlays = pyqtSignal(str, str)
    def __init__(self, plays = {}, subDevDict=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.dataBase = QSqlDatabase.addDatabase("QSQLITE", OrganizedPlay.sqlDatabaseConntionName)
        self.dataBase.setDatabaseName(DataBase.dataBaseName)
        self.dataBase.setUserName("root")
        self.dataBase.setPassword("123456")
        if self.dataBase.open():pass
        else:
            print("opened failure")
        self.setWindowTitle(self.tr("编辑剧目"))
        self.subDevDict = subDevDict
        self.returnPushButton.setDefault(True)
        # add plays
        self.contentLayout = QVBoxLayout()
        self.contentListWidget = ListWidget()
        self.contentLayout.addWidget(self.contentListWidget)
        for play in plays.items():
            item = PlaysListWidgetItem(sId=play[0], playName=play[1], QIcon=QIcon(":/images/images/dirpic.jpg"))
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
        self.insertPlays.emit(widget.text(), widget.selfId)
    def onEditingPushButtonClicked(self):
        playsItem = self.contentListWidget.currentItem()
        if playsItem is None:
            QMessageBox.warning(self, "Warning", self.tr("请选中要编辑的剧目"), QMessageBox.Ok)
        else:
            sqlQuery = QSqlQuery(QSqlDatabase.database(OrganizedPlay.sqlDatabaseConntionName))
            sqlQuery.exec_("""SELECT * FROM SceneInfo WHERE parentIndex={}""".format(playsItem.selfId))
            rec = sqlQuery.record()
            nameCol = rec.indexOf("sceneName")
            indexCol = rec.indexOf("selfIndex")
            sceneDict = {}
            while sqlQuery.next():
                sceneDict[sqlQuery.value(indexCol)] = sqlQuery.value(nameCol)
            editingScene = EditingSceneAction(subDevDict=self.subDevDict, pId=playsItem.selfId, scenes=sceneDict)
            editingScene.resize(600, 300)
            editingScene.exec_()

    def onContentListWidgetItemDoubleClicked(self, widget):
        self.onEditingPushButtonClicked()

    def onNewPushButtonClicked(self):
        widget = self.contentListWidget.currentItem()# cancel selected.
        if widget:
            widget.setSelected(False)
        new = NewAction(title="编辑剧目", tips="剧目名称:")
        if new.exec_():
            try:
                scenes = {}
                for s in range(new.quantitySpinBox.value()):
                    scenes[s]=[]
                id = QDateTime.currentDateTime().toString("yyyyMMddhhmmsszzz") + str(random.randint(0,100))
                item = PlaysListWidgetItem(sId=id, playName=new.nameLineEdit.text(), QIcon=QIcon(":/images/images/dirpic.jpg"))
                self.insertPlays.emit(new.nameLineEdit.text(), id)
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

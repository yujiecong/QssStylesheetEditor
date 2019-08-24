﻿# -*- coding: utf-8 -*-

import sys,os

os.chdir(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import (QApplication, qApp, QMainWindow, QWidget, QLabel, QPushButton,
                             QColorDialog, QFileDialog, QMessageBox,QSizePolicy)
from PyQt5.QtGui import QIcon, QColor, qGray,QFont
from PyQt5.QtCore import Qt,QSize
# import sip

from ui import Widgets_MainWin
from ui.flow_layout import QFlowLayout
from QssTemplate import Qsst

class MainWin(QMainWindow, Widgets_MainWin):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.title=self.tr("QssStylesheetEditor v1.1")
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("img/colorize.ico"))
        self.qsst = Qsst()
        self.clrBtnDict = {}
        self.file=None
        self.lastSavedText=""
        self.newIndex=0
        self.__lastKeyTextChanged=False#如果上一次按键文本改变了，那么鼠标，方向键都会导致重新渲染

        self.setupUi(self)
        self.setupActions()
        self.new()
        self.statusbar.showMessage("Ready")

    def setupActions(self):
        #theme  toolbarWidget
        self.actions["DisableQss"].toggled.connect(self.unuseQss)
        self.themeCombo.currentTextChanged.connect(qApp.setStyle)

        #menubar toolbar
        self.actions["new"].triggered.connect(self.new)
        self.actions["open"].triggered.connect(self.open)
        self.actions["save"].triggered.connect(self.save)
        self.actions["saveas"].triggered.connect(self.saveAs)
        self.actions["export"].triggered.connect(self.export)
        self.actions["undo"].triggered.connect(self.editor.undo)
        self.actions["redo"].triggered.connect(self.editor.redo)
        self.actions["cut"].triggered.connect(self.editor.cut)
        self.actions["copy"].triggered.connect(self.editor.copy)
        self.actions["paste"].triggered.connect(self.editor.paste)
        self.actions["ShowColor"].triggered.connect(self.docks["color"].setVisible)
        self.actions["ShowPreview"].triggered.connect(self.docks["preview"].setVisible)

        # contianerWidget.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Minimum)
        def sizeDock(dockLoc):
            if(dockLoc==Qt.TopDockWidgetArea or dockLoc==Qt.BottomDockWidgetArea):
                #self.colorPanelWidget.resize(self.docks["color"].width(),self.colorPanelLayout.minimumSize().height())
                self.docks["color"].widget().resize(self.docks["color"].width(),self.colorPanelLayout.minimumSize().height())
        self.docks["color"].dockLocationChanged.connect(sizeDock)

        #main editor
        self.editor.keyPress.connect(self.textChanged)
        def rend():
            self.renderStyle()
            self.loadColorPanel()
        self.editor.loseFocus.connect(rend)
        self.editor.mouseLeave.connect(rend)
        self.editor.mousePress.connect(rend)

    def unuseQss(self,unuse):
        if(unuse):
            self.setStyleSheet('')
            self.themeCombo.setEnabled(True)
        else:
            self.renderStyle()
            self.loadColorPanel()
            self.themeCombo.setEnabled(False)

    def renderStyle(self):
        self.qsst.srctext = self.editor.text()
        self.qsst.loadVars()
        self.qsst.convertQss()

        norand=self.actions["DisableQss"].isChecked()
        if(norand):
            self.setStyleSheet('')
        else:
            self.setStyleSheet(self.qsst.qss)


    def textChanged(self, e):  # QKeyEvent(QEvent.KeyPress, Qt.Key_Enter, Qt.NoModifier)
        #if (32<e.key()<96 or 123<e.key()<126 or 0x1000001<e.key()<0x1000005 or e.key==Qt.Key_Delete):
        if(not self.editor.isModified()):
            self.editor.setModified(True)
            self.setWindowTitle(self.title+" - *" + os.path.basename(self.file))
            self.actions["save"].setEnabled(True)

        if (e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter #大键盘为Ret小键盘为Enter
            or e.key() == Qt.Key_Semicolon or e.key() == Qt.Key_BraceRight or e.key() == Qt.Key_Tab
            or e.key() == Qt.Key_Up or e.key() == Qt.Key_Down or e.key() == Qt.Key_Left or e.key() == Qt.Key_Right):
            self.renderStyle()
            self.loadColorPanel()
            self.__lastKeyTextChanged = False
        else:
            self.__lastKeyTextChanged = True

    def loadColorPanel(self):
        self.qsst.srctext = self.editor.text()
        self.qsst.loadVars()

        #item = self.colorGridLayout.itemAt(0)
        # while (item != None):
        #     self.colorGridLayout.removeItem(item)
        #     # self.colorGridLayout.removeWidget(item.widget())
        #     # item.widget().setParent(None)#这三行没有作用
        #     sip.delete(item.widget())  # 虽然控件删除了，但是grid的行数列数没减少，但是不影响使用
        #     sip.delete(item)
        #     item = self.colorGridLayout.itemAt(0)
        # self.colorGridLayout.update()  # 不起作用

        #a,b=list(self.clrBtnDict.keys()),list(self.qsst.varDict.keys());a.sort();b.sort()
        if(sorted(list(self.clrBtnDict.keys()))!=sorted(list(self.qsst.varDict.keys()))):
            while(self.colorPanelLayout.count()>0):
                self.colorPanelLayout.removeItem(self.colorPanelLayout.itemAt(0))
            self.clrBtnDict = {}
            for varName, clrStr in self.qsst.varDict.items():
                contianerWidget = QWidget()
                contianerWidget.setMinimumSize(QSize(180,25))
                label = QLabel(varName, contianerWidget)
                label.setFont(QFont("Arial",9,QFont.Medium))
                btn = QPushButton(clrStr, contianerWidget)
                self.clrBtnDict[varName] = btn
                label.setFixedWidth(80)
                btn.setFixedWidth(100)
                label.move(5,10)
                btn.move(80,5)
                self.colorPanelLayout.addWidget(contianerWidget)
                self.colorPanelLayout.setSpacing(5)
                btn.clicked.connect(lambda x, var=varName: self.chclr(var))

        for varName,btn in self.clrBtnDict.items():
            clrStr=self.qsst.varDict[varName]
            btn.setText(clrStr)
            if ("rgb" in clrStr):
                t = clrStr.strip(r" rgba()")
                c = t.split(',')
                if (len(c) > 3):
                    lable = c[3]
                else:
                    lable = 255
                color = QColor(c[0],c[1], c[2], lable)
            else:
                color = QColor(clrStr)
            s = ''
            if (qGray(color.rgb()) < 100):
                s += "color:white;"

            btn.setStyleSheet(s + "background:" + btn.text())

    def chclr(self, var):
        color = QColorDialog.getColor(Qt.white, self, "color pick", QColorDialog.ShowAlphaChannel)
        if (color.isValid()):
            s = ''
            clrstr=color.name()
            if (color.alpha() == 255):
                clrstr = color.name()
            else:
                clrstr = color.name(QColor.HexArgb)#'rgba({},{},{},{})'.format(color.red(), color.green(), color.blue(), color.alpha())
            #     s = 'font-size:8px;'
            if (qGray(color.rgb()) < 100):
                s += 'color:white;'
            self.clrBtnDict[var].setText(clrstr)
            self.clrBtnDict[var].setStyleSheet(s + "background:" + clrstr)
            self.qsst.varDict[var] = clrstr
            self.qsst.writeVars()
            self.editor.setText(self.qsst.srctext)
            self.renderStyle()

    def open(self,_=None, file=None):#_参数用于接收action的event参数,bool类型
        if (file is None):
            file, _ = QFileDialog.getOpenFileName(self, "Open File", file,
                                                  "QSS(*.qss *.qsst);;qsst(*.qsst);;qss(*.qss);;all(*.*)")#_是filefilter
        if (os.path.exists(file)):
            self.file=file
            self.lastSavedText = self.editor.text()
            self.editor.load(self.file)
            self.renderStyle()
            self.loadColorPanel()
            self.setWindowTitle(self.title+" - " + os.path.basename(file))

    def new(self):
        if(self.editor.isModified()):
            ret=QMessageBox.question(self,"Qss Template Editer","当前文件尚未保存，是否要保存文件？",
                                     QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel,QMessageBox.No)
            if(ret==QMessageBox.Yes):
                self.save()
            elif(ret==QMessageBox.Cancel):
                return

        self.open(file="data/default.qsst")
        self.newIndex=self.newIndex+1
        self.file="new{}.qsst".format(self.newIndex)
        self.setWindowTitle(self.title+" - " + os.path.basename(self.file))
        self.editor.setModified(False)

    def save(self):
        if (self.file and os.path.exists(self.file)):
            self.lastSavedText=self.editor.text()
            self.editor.save(self.file)
            self.setWindowTitle(self.title+" - " + os.path.basename(self.file))
            self.actions["save"].setEnabled(False)
        else:
            self.saveAs()

    def saveAs(self):
        # f="." if self.file==None else self.file
        file, filefilter = QFileDialog.getSaveFileName(self, "save file", self.file, "qsst(*.qsst);;qss(*.qss);;all(*.*)")
        if (file):
            self.file = file
            self.lastSavedText=self.editor.text()
            self.editor.save(self.file)
            self.setWindowTitle(self.title+" - " + os.path.basename(file))
            self.actions["save"].setEnabled(False)

    def export(self):
        self.qsst.convertQss()
        if(self.file==None):
            f="."
        else:
            #f=self.file[:-1]
            f=os.path.splitext(self.file)[0]
        file, _ = QFileDialog.getSaveFileName(self, "export Qss", f, "Qss(*.qss);;all(*.*)")
        if file:
            with open(file, 'w', newline='') as f:
                f.write(self.qsst.qss)

    def closeEvent(self, e):
        if(self.editor.isModified()):
            if(self.lastSavedText!=self.editor.text()):
                msg=QMessageBox(QMessageBox.Question,"Qss Style Editor",self.tr("是否将更改保存到"+os.path.basename(self.file)),
                                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
                msg.setDefaultButton(QMessageBox.Discard)
                msg.button(QMessageBox.Save).setText(self.tr("保存"))
                msg.button(QMessageBox.Discard).setText(self.tr("放弃"))
                msg.button(QMessageBox.Cancel).setText(self.tr("取消"))
                ret=msg.exec_()
                # ret=QMessageBox.information(self,"Qss Style Editor",self.tr("是否将更改保存到"+os.path.basename(self.file)),
                #                             QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel,QMessageBox.Yes)
                if(ret==QMessageBox.Save or ret==QMessageBox.Yes):
                    self.save()
                    e.ignore()
                elif(ret==QMessageBox.Discard or ret==QMessageBox.No):
                    qApp.exit()
                else:
                    e.ignore()

def main():
    sys.setrecursionlimit(1500)
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())


main()

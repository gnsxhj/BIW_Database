#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :ProjectList.py
# @Time      :2020/10/3 19:07
# @Author    :
from PyQt5.QtWidgets import QApplication, QDialog,QCheckBox
from PyQt5 import QtCore
from PyQt5 import uic
from numpy import array
import re
class ProjectList(QDialog):
    def __init__(self,tablelist):
        super().__init__()
        self.ui = uic.loadUi("gui/ProjectList.ui")
        self.ui.B_OK.clicked.connect(self.fun_accept)
        self.ui.B_Cancel.clicked.connect(self.fun_cancel)
        self.projectlist = []
        self.showitem(tablelist)
    def showitem(self,tablelist):
        i =40
        for item in tablelist:
            item2 = tuple(item)
            self.addcheckbotton(item)
            self.ui.chkbox.move(10,i)
            i+=30
            self.ui.chkbox.stateChanged.connect(self.checkLanguage)
            #self.ui.chkbox.setChecked(True)
    def checkLanguage(self,state):
        checkBox = self.sender()
        name = checkBox.text().split(",")[0][2:-1]
        #print(array(checkBox.text()))
        if state == QtCore.Qt.Unchecked:
            self.projectlist.remove(name)
        elif state == QtCore.Qt.Checked:
            self.projectlist.append(name)
    def addcheckbotton(self,name):
        self.ui.chkbox = QCheckBox(name, self.ui.scrollArea)
    def fun_accept(self):
        self.ui.accept()
    def fun_cancel(self):
        self.projectlist = []
        self.ui.reject()

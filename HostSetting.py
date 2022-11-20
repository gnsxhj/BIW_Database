#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :HostSetting.py
# @Time      :2021/1/9 21:12
# @Author    :
from PyQt5.QtWidgets import  QDialog
from PyQt5 import uic
class Host(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("gui/HostSetting_Dialog.ui")
        self.ui.B_OK.clicked.connect(self.F_Accept)
    def F_Accept(self):
        self.host = self.ui.E_Host.text()
        self.ui.accept()
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Login.py
# @Time      :2020/10/3 14:53
# @Author    :
import sys
from PyQt5.QtWidgets import  QDialog
from PyQt5 import uic
#from config import userlist
from Dao import dao
from HostSetting import Host


class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("gui/Login_Dialog.ui")
        #self.ui = uic.loadUi("gui_database.ui")
        self.ui.closeEvent = self.closeEvent
        self.ui.B_Login.clicked.connect(self.fun_accept)
        self.ui.B_Cancel.clicked.connect(self.fun_cancel)
        self.ui.B_Setting.clicked.connect(self.F_Setting)
        self.F_Auto_Setting()
    def fun_accept(self):
        self.name = self.ui.E_Username.text()
        self.password = self.ui.E_Password.text()
        #账号判断
        if self.name == "":
            return
        # 密码判断
        if self.password == "":
            return
        try:
            self.mydao = dao(self.name,self.password,self.host)
            con = self.mydao.con
            self.ui.accept()
        except:
            self.ui.E_Password.setText("")
            return
    def fun_cancel(self):
        self.ui.E_Username.setText("")
        self.ui.E_Password.setText("")
    def closeEvent(self,event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        try:
            sys.exit()
        finally:
            try:
                self.mydao.con.close()
            except:
                pass
    def F_Setting(self):
        myhost = Host()
        result = myhost.ui.exec_()
        myhost.ui.show()
        if result == QDialog.Accepted:
            self.host = myhost.host
    def F_Auto_Setting(self):
        myhost = Host()
        self.host = myhost.ui.E_Host.text()

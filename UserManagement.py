#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :UserManagement.py
# @Time      :2020/11/1 13:37
# @Author    :
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QFileDialog,QTreeWidgetItem
from PyQt5 import uic

#from config import userlist, path

class UserManage(QDialog):
    def __init__(self,admin=[],user=[],visitor=[]):
        super().__init__()
        self.ui = uic.loadUi("gui/UserList.ui")
        self.alluser = admin+user+visitor
        self.ui.B_CreateUser.clicked.connect(self.F_CreateUser)
        self.ui.B_DeleteUser.clicked.connect(self.F_DeleteUser)
        #self.ui.B_Apply.clicked.connect(self.F_Apply)
        self.ui.B_OK.clicked.connect(self.ui.accept)
        self.ui.B_Cancel.clicked.connect(self.ui.reject)
        self.Userlist(admin,user,visitor)
        self.ui.Tree_UserList.expandAll()
        self.ui.Tree_UserList.clicked.connect(self.F_UserListTree)
        self.create = []
        self.create2 = []
        self.delete = []
    def F_Apply(self):
        QDialog.Accepted.emit()
    def F_CreateUser(self):
        UserType = self.ui.Combo_UserType.currentText()
        UserName = self.ui.E_UserName.text()
        Password = self.ui.E_Password.text()
        if UserName in self.alluser:
            print("{} already exists!".format(UserName))
        else:
            self.alluser.append(UserName)
            if UserName in self.delete:
                self.create2.append((UserName,UserType,Password))
            else:
                self.create.append((UserName,UserType,Password))
        if UserType == "Admin":
            child = QTreeWidgetItem(self.Admin)
            child.setText(0,UserName)
        if UserType == "User":
            child = QTreeWidgetItem(self.User)
            child.setText(0,UserName)
        if UserType == "Visitor":
            child = QTreeWidgetItem(self.Visitor)
            child.setText(0,UserName)
    def F_DeleteUser(self):
        name = self.ui.E_NametoDelete.text()
        if name in self.alluser:
            self.delete.append(name)
            self.alluser.remove(name)
            self.parent.removeChild(self.item)
        else:
            print("{} doesn't exist!".format(name))
    def Userlist(self,admin,user,visitor):
        self.ui.Tree_UserList.setColumnCount(1) #设置列数
        self.ui.Tree_UserList.setHeaderLabels(['UserList'])#设置树形控件头部的标题
        self.Admin = QTreeWidgetItem(self.ui.Tree_UserList)
        self.Admin.setText(0,'Admin')
        self.User = QTreeWidgetItem(self.ui.Tree_UserList)
        self.User.setText(0, 'User')
        self.Visitor = QTreeWidgetItem(self.ui.Tree_UserList)
        self.Visitor.setText(0, 'Visitor')
        for item in admin:
            child = QTreeWidgetItem(self.Admin)
            child.setText(0, item)
        for item in user:
            child = QTreeWidgetItem(self.User)
            child.setText(0, item)
        for item in visitor:
            child = QTreeWidgetItem(self.Visitor)
            child.setText(0, item)
    def F_UserListTree(self):
        self.item = self.ui.Tree_UserList.currentItem()
        self.parent = self.item.parent()
        self.ui.E_NametoDelete.setText(self.item.text(0))
        pass

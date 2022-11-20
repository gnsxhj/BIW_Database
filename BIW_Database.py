#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :BIW_Database.py
# @Time      :2020/10/3 14:57
# @Author    :
import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow,QMessageBox,QFileDialog
from PyQt5 import uic
import sip
import time
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5

from ImportProject import NewProject

from Login import Login
from TableViewModel import pandasModel
from ProjectList import ProjectList
from UserManagement import UserManage
from Figure import MyFigure
#from config import path

class DB(QMainWindow):
    def __init__(self,mydao):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        super().__init__()
        self.ui = uic.loadUi("gui/gui_database.ui")
        self.ui.V_Output.setSortingEnabled(True)
        #self.ui.B_ImportProject.clicked.connect(self.F_ImportNewProject)
        self.ui.B_SelectProject.clicked.connect(self.F_SelectProject)
        self.ui.B_Query.clicked.connect(self.F_Query)
        #self.ui.B_OutputProject.clicked.connect(self.F_OutputProject)
        #self.ui.B_DeleteProject.clicked.connect(self.F_DeleteProject)
        self.ui.B_UserDefine.clicked.connect(self.F_UserDefine)
        self.ui.B_CancelUserDefine.clicked.connect(self.ui.T_UserDefine.clear)
        #self.ui.B_ManageUser.clicked.connect(self.F_ManageUser)
        self.ui.B_ClearQuery.clicked.connect(self.F_ClearQuery)
        self.ui.B_UserDefineImport.clicked.connect(self.F_UserDefineImport)
        self.ui.B_UserDefineSave.clicked.connect(self.F_UserDefineSave)
        self.ui.actionImport.triggered.connect(self.F_ImportNewProject)
        self.ui.actionExport.triggered.connect(self.F_OutputProject)
        self.ui.actionDelete.triggered.connect(self.F_DeleteProject)
        self.ui.actionManage.triggered.connect(self.F_ManageUser)
        self.mydao = mydao
        self.projectlist = []
        self.ui.closeEvent = self.closeEvent
        self.F1 = MyFigure()
        self.F2 = MyFigure()
        self.F3 = MyFigure()
        self.ui.V_Number_Layout.addWidget(self.F1)
        self.ui.V_Weight_Layout.addWidget(self.F2)
        #self.ui.V_Ratio_Layout.addWidget(self.F3)
    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """

        reply = QMessageBox.question(self,
                                               'BIW',
                                               "Do you want to quit？",
                                               QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            self.mydao.con.close()
        else:
            event.ignore()

    def F_ImportNewProject(self):
        try:
            newpro = NewProject()
            newpro.ui.show()
            result=newpro.ui.exec_()
            if result == QDialog.Accepted:

                self.mydao.createtable("project_db",newpro.colname)#创建项目表
                df4 = self.mydao.insertalltable("project_db",newpro.ProjectName,newpro.colname,newpro.newtable)#在项目表中写入数据
                key = ("project_name","configuration","date")
                value = (newpro.ProjectName,newpro.Configuration,newpro.Date)
                self.mydao.insertiterm("project_list",key,value)#先创建project list,并写入新增数据
                if df4:
                    pdmodel = pandasModel(df4)
                    self.ui.V_Output.setModel(pdmodel)
                    self.ui.T_Message.append(">>Project is imported!")
                else:
                    self.ui.T_Message.append(">>Fail to Import!")
            else:
                pass
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def SF_ShowProjectlist(self):
        try:
            tablelist = self.mydao.showallitem("project_list")#显示project list中所有的内容，二维数组
            self.newlist = []
            for item in tablelist:
                self.newlist.append(str(item)) #把tuple(项目名称，本表配置，数据日期) 转为str
            self.pl = ProjectList(self.newlist)
            self.pl.ui.show()
            result = self.pl.ui.exec_()
            return result
        except Exception as e:
            print(e)
    def F_SelectProject(self):
        try:
            result=self.SF_ShowProjectlist()
            if result == QDialog.Accepted:
                self.ui.T_Message.append(">> You have selected:")
                self.projectlist = self.pl.projectlist
                for item in self.projectlist:
                    self.ui.T_Message.append(item)
            if result == QDialog.Rejected:
                self.projectlist = self.pl.projectlist
                self.ui.T_Message.append(">> Query will be in all projects.")
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_Query(self):
        try:
            def Decimal(s):
                return int(s)
            signal=[0,1,1]
            if self.ui.C_AllItem.isChecked():
                signal[0]=1
            # if self.ui.C_NumberItem.isChecked():
            #     signal[1]=1
            # if self.ui.C_TotalWeight.isChecked():
            #     signal[2]=1
            self.querywhere=self.F_QueryList()#where 后所有的查询条件
            if self.querywhere == "s_strength":
                self.SF_sum_query(type="strength")
            elif self.querywhere == "s_cladding":
                self.SF_sum_query(type="cladding")
            else:
                result = self.mydao.query("project_db",self.querywhere,signal,self.QueryProject)
                #print("res: ",result)
                df = result[0]
                pdmodel = pandasModel(df)
                self.ui.V_Output.setModel(pdmodel)

                if signal[1] == 1:
                    amount = self.SF_plotbar_number(result[1])
                    self.ui.T_Message.append(">>>>Total number is : {} ".format(amount))
                if signal[2] == 1:
                    weight = self.SF_plotbar_weight(result[2])
                    self.ui.T_Message.append(">>>>Total weight is : {}".format(weight))
                if signal[1] ==1 and signal[2] ==1:
                    self.SF_plotpie(result[1],result[2],result[3],result[4])
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def SF_sum_query(self,type):
        try:
            QueryList = []
            if len(self.projectlist) == 1:
                project = self.F_QueryProject(self.projectlist)
                result = self.mydao.query_sum(type,project)
                df = result[0]
                pdmodel = pandasModel(df)
                self.ui.V_Output.setModel(pdmodel)#显示表格

                label = list(map((lambda x: x[1]),result[1]))
                amount = list(map((lambda x: x[2]),result[1]))
                weight = list(map((lambda x: x[3]),result[1]))
                try:# 把原来的图形清除
                    for i in range(self.ui.V_Ratio_Layout.count()):
                        self.ui.V_Ratio_Layout.itemAt(i).widget().deleteLater()
                        sip.delete(self.ui.V_Ratio_Layout.itemAt(i).widget())
                    for i in range(self.ui.V_Number_Layout.count()):
                        self.ui.V_Number_Layout.itemAt(i).widget().deleteLater()
                        sip.delete(self.ui.V_Number_Layout.itemAt(i).widget())
                    for i in range(self.ui.V_Weight_Layout.count()):
                        self.ui.V_Weight_Layout.itemAt(i).widget().deleteLater()
                        sip.delete(self.ui.V_Weight_Layout.itemAt(i).widget())
                except Exception as e:
                    self.ui.T_Message.append(str(e))
                # 下面依次显示number/weight/ratio
                self.F1 = MyFigure()
                self.F1.plotbar(amount, label, "number")
                self.ui.V_Number_Layout.addWidget(self.F1)
                self.F2 = MyFigure()
                self.F2.plotbar(weight, label, "weight")
                self.ui.V_Weight_Layout.addWidget(self.F2)
                self.F3 = MyFigure()
                self.F3.plotpiesum(amount,weight,label)
                self.ui.V_Ratio_Layout.addWidget(self.F3)
            else:
                self.ui.T_Message.append(">>>>ERROR: Please select one (only one） project!")
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def SF_plotpie(self,num,wei,sum_num,sum_wei):
        try:
            number = list(map((lambda x: x[1]), num))
            num_label = list(map((lambda x: x[0]), num))
            weight = list(map((lambda x: x[1]), wei))
            sum_num = list(map((lambda x: x[1]), sum_num))
            other_num = list(map((lambda i:i[1]-i[0]),zip(number,sum_num)))
            sum_wei = list(map((lambda x: x[1]), sum_wei))
            other_wei = list(map((lambda i: i[1] - i[0]), zip(weight, sum_wei)))
        except Exception as e: #如果出错，大概率是sql语法出错，即检索条件输入的格式错误
            self.ui.T_Message.append(">> Wrong format!")
            self.ui.T_Message.append(str(e))
            return
        finally:
            try:
                for i in range(self.ui.V_Ratio_Layout.count()):
                    self.ui.V_Ratio_Layout.itemAt(i).widget().deleteLater()
                    sip.delete(self.ui.V_Ratio_Layout.itemAt(i).widget())
            except Exception as e:
                print(e)
        if not num:
            self.ui.T_Message.append(">>>>search result: empty! no ratio Graph！")
        else:
            try:
                self.F3 = MyFigure()
                self.F3.plotpie(number,other_num,weight,other_wei,num_label)
                self.ui.V_Ratio_Layout.addWidget(self.F3)
            except Exception as e:
                print(e)

    def SF_plotbar_number(self,result):
        try:
            amount = list(map((lambda x: x[1]), result))
            label = list(map((lambda x: x[0]), result))
        except:
            return
        finally:
            try:
                for i in range(self.ui.V_Number_Layout.count()):
                    self.ui.V_Number_Layout.itemAt(i).widget().deleteLater()
                    sip.delete(self.ui.V_Number_Layout.itemAt(i).widget())
            except Exception as e:
                print(e)
        if not amount:
            self.ui.T_Message.append(">>>>search result: empty!")
        else:
            try:
                self.F1 = MyFigure()
                self.F1.plotbar(amount, label,"number")
                self.ui.V_Number_Layout.addWidget(self.F1)
                return amount
            except Exception as e:
                print(e)
    def SF_plotbar_weight(self,result):
        try:
            amount = list(map((lambda x: x[1]), result))
            label = list(map((lambda x: x[0]), result))
        except:
            return
        finally:
            try:
                for i in range(self.ui.V_Weight_Layout.count()):
                    self.ui.V_Weight_Layout.itemAt(i).widget().deleteLater()
                    sip.delete(self.ui.V_Weight_Layout.itemAt(i).widget())
            except Exception as e:
                print(e)
        if not amount:
            self.ui.T_Message.append(">>>>search result: empty!")
        else:
            try:
                self.F2 = MyFigure()
                self.F2.plotbar(amount, label,"weight (g)")
                self.ui.V_Weight_Layout.addWidget(self.F2)
                return amount
            except Exception as e:
                print(e)
    def F_QueryList(self):
        self.QueryList = []
        project = self.F_QueryProject(self.projectlist)
        if project:
            project="("+project+")"
            self.QueryList.append(project)
        part = self.ui.E_PartName.text().strip()
        if part:
            #QueryPart = "(PartName='{0}' or ShortPartName='{0}')".format(part)
            QueryPart = "(PartName regexp '{}')".format(part)
            self.QueryList.append(QueryPart)
        set = self.ui.E_Set.text().strip()
        if set:
            QuerySet = "(SetGroup regexp '{}')".format(set)
            self.QueryList.append(QuerySet)
        Material = self.ui.E_Material.text().strip()
        if Material:
            QueryMaterial = "(Material regexp '{}')".format(Material)
            self.QueryList.append(QueryMaterial)
        Thickness = self.ui.E_Thickness.text().strip()
        if Thickness:
            QueryThickness="Thickness{}".format(Thickness)
            self.QueryList.append(QueryThickness)
        Weight = self.ui.E_Weight.text().strip()
        if Weight:
            QueryWeight="Weight {}".format(Weight)
            self.QueryList.append(QueryWeight)
        Strength = self.ui.E_Strength.text().strip()
        if Strength:
            if Strength == "S" or Strength == "s":
                querywhere = "s_strength"
                return querywhere

            else:
                QueryStrength="Strength{}".format(Strength)
                self.QueryList.append(QueryStrength)
        Cladding = self.ui.E_Cladding.text().strip()
        if Cladding:
            if Cladding == "S" or Cladding == "s":
                querywhere = "s_cladding"
                return querywhere
            else:
                QueryCladding="(Cladding regexp '{}')".format(Cladding)
                self.QueryList.append(QueryCladding)
        Supplier = self.ui.E_Supplier.text().strip()
        if Supplier:
            QuerySupplier="(Supplier regexp'{}')".format(Supplier)
            self.QueryList.append(QuerySupplier)
        Class = self.ui.E_Class.text().strip()
        if Class:
            QueryClass = "(Class regexp'{}')".format(Class)
            self.QueryList.append(QueryClass)
        Pfeil = self.ui.E_Pfeil.text().strip()
        if Pfeil:
            QueryPfeil = "(Pfeil regexp'{}')".format(Pfeil)
            self.QueryList.append(QueryPfeil)
        Name = self.ui.E_Name.text().strip()
        if Name:
            QueryName = "(DeutschName regexp '{0}' or CNName regexp '{0}')".format(Name)
            self.QueryList.append(QueryName)
        querywhere = " and ".join(self.QueryList)
        return querywhere
    def F_QueryProject(self,projectlist):
        try:
            self.QueryProject = ""
            if projectlist:
                i=0
                while i<100:
                    try:
                        if i==0:
                            self.QueryProject = "project_db='{}'".format(projectlist[i])
                        else:
                            Querytemp = "project_db='{}'".format(projectlist[i])
                            self.QueryProject = self.QueryProject + " or " + Querytemp
                        i+=1
                    except :
                        break
            else:
                pass
            return(self.QueryProject) #返回 str，格式 project_db='vw418' or project_db='AU516' or project_db='sk312'
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_UserDefine(self):
        """用户自定义语句可以用多个sql语句组成，用；分隔，V—Output显示最后一个的查询结果"""
        try:
            sqls = self.ui.T_UserDefine.toPlainText().split(";")
            for sql in sqls:
                result = self.mydao.userdefine(sql)
                #(type(result))
                if isinstance(result,str):
                    self.ui.T_Message.append(result)
                else:
                    pdmodel = pandasModel(result)
                    self.ui.V_Output.setModel(pdmodel)
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_OutputProject(self):
        try:
            result = self.SF_ShowProjectlist()
            if result == QDialog.Accepted:
                self.ui.T_Message.append(">> The following projects will be output:")
                projectlist = self.pl.projectlist
                for item in projectlist:
                    self.ui.T_Message.append(item)
            if result == QDialog.Rejected:
                projectlist = []

            if projectlist:
                signal = [1,0,0]
                path_dir = QFileDialog.getExistingDirectory(self, "Export to Excel", "")
                for item in projectlist:
                    querywhere = "project_db='{}'".format(item)
                    result = self.mydao.query("project_db",querywhere,signal,self.QueryProject)
                    df = result[0]
                    df.drop('seq', axis=1, inplace=True)
                    pdmodel = pandasModel(df)
                    self.ui.V_Output.setModel(pdmodel)
                    df.drop('project_db',axis=1, inplace=True)
                    file = os.path.join(path_dir, '{}.xlsx'.format(item))
                    writer = pd.ExcelWriter(file,engine='xlsxwriter')
                    df.to_excel(writer, sheet_name='Gewichtliste', startrow=2, header=2, index=False)
                    writer.save()
                    self.ui.T_Message.append(">>{0} has been output : {1}".format(item,file))
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_DeleteProject(self):
        try:
            result = self.SF_ShowProjectlist()
            if result == QDialog.Accepted:
                projectlist = self.pl.projectlist
            if result == QDialog.Rejected:
                projectlist = self.pl.projectlist
            if projectlist:
                for item in projectlist:
                    e = self.mydao.deleteproject(item)
                    self.ui.T_Message.append(str(e))
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_ManageUser(self):
        #print(admin,user,visitor)
        try:
            admin, user, visitor = [], [], []
            res = self.mydao.UserList()
            # print(res)
            if res[0]:
                admin = [item[0] for item in res[0]]
            if res[1]:
                user = [item[0] for item in res[1]]
            if res[2]:
                visitor = [item[0] for item in res[2]]
            UserM = UserManage(admin,user,visitor)
            UserM.ui.show()
            result = UserM.ui.exec_()

            if result == QDialog.Accepted:
                if UserM.create:
                    for item in UserM.create:
                        self.mydao.CreateUser(item)
                if UserM.delete:
                    for item in UserM.delete:
                        self.mydao.DeleteUser(item)
                if UserM.create2:
                    for item in UserM.create2:
                        self.mydao.CreateUser(item)
            else:
                pass
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_UserDefineImport(self):
        try:
            path_tuple = QFileDialog.getOpenFileName(self, "Open file dialog", "./", "")
            path = path_tuple[0]
            with open(file=path, mode='r', encoding='utf-8') as file:
                con = file.read()
                self.ui.T_UserDefine.clear()
                self.ui.T_UserDefine.append(str(con))
        except Exception as e:
            self.ui.T_Message.append(str(e))
    def F_UserDefineSave(self):
        try:
            path_tuple = QFileDialog.getSaveFileName(self, "Save sql in text", "*.txt")
            path = path_tuple[0]
            with open(file=path, mode='w', encoding='utf-8') as file:
                s = self.ui.T_UserDefine.toPlainText()
                file.write(str(s))
            res = ">>{} has been saved!".format(path)
            self.ui.T_Message.append(res)
        except Exception as e:
            self.ui.T_Message.append(str(e))

    def F_ClearQuery(self):
        self.projectlist = []
        self.ui.E_PartName.setText('')
        self.ui.E_Material.setText('')
        self.ui.E_Strength.setText('')
        self.ui.E_Thickness.setText('')
        self.ui.E_Weight.setText('')
        self.ui.E_Pfeil.setText('')
        self.ui.E_Set.setText('')
        self.ui.E_Cladding.setText('')
        self.ui.E_Supplier.setText('')
        self.ui.E_Name.setText('')
        self.ui.E_Class.setText('单件')




if __name__ == "__main__":
    app = QApplication(sys.argv)
    Mylogin=Login()
    Mylogin.ui.show()
    if Mylogin.ui.exec_() == QDialog.Accepted:
        MyDB=DB(Mylogin.mydao)
        MyDB.ui.show()
    sys.exit(app.exec_())
    #

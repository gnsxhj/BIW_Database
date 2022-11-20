#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Dao.py
# @Time      :2020/10/2 22:56
# @Author    :
import pandas as pd
import mysql.connector.pooling
from config import sqlconfig
class dao(object):
    def __init__(self,name,password,host):
        self.sqlconfig = sqlconfig.sql
        self.sqlconfig["user"] = name
        self.sqlconfig["password"] = password
        self.sqlconfig["host"] = host
        try:
            pool = mysql.connector.pooling.MySQLConnectionPool(**self.sqlconfig, pool_size=2)
            self.con = pool.get_connection()
        except Exception as e:
            print(e)
    def createtable(self,name,colname):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()  # 创建连接
            sql = "CREATE TABLE IF NOT EXISTS {0}  ({1} INT AUTO_INCREMENT PRIMARY KEY,"\
            "{2} VARCHAR(80), {3} VARCHAR(80)," \
              " {4} VARCHAR(200),{5} VARCHAR(200),{6} VARCHAR(80),{7} VARCHAR(80)," \
              "{8} INT,{9} VARCHAR(100), {10} VARCHAR(80),{11} VARCHAR(80)," \
              "{12} INT,{13} FLOAT, {14} VARCHAR(80),{15} VARCHAR(80), {16} VARCHAR(80)," \
              "{18} VARCHAR(200), {17} INT, {0} VARCHAR(200) );".format(name, "seq",*colname)
            cursor.execute(sql)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()


    def insertalltable(self,TableName,Proname,colname,df):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()  # 创建连接
            df2 = pd.DataFrame(df.values.T, index=df.columns, columns=df.index)
            df3 = pd.DataFrame(df2.values)
            for i in range(df2.shape[1]):
                for k in range(len(df2[i])):
                    if k == 6 or k==10 or k==15:
                        df3[i][k] = int(df2[i][k])  #下级零件数\数量\强度等级为INT
                    elif k == 11 :
                        df3[i][k] = float(df2[i][k])#重量为float
                    else:
                        df3[i][k] = str(df2[i][k])
                value = tuple(list(df2[i])+[Proname])
                colname = tuple(list(colname) + [TableName])
                sql = "INSERT INTO {0}({2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12}," \
                      "{13},{14},{15},{16},{17},{18},{19}) VALUES{1}".format(TableName,value,*colname)
                #print(sql)
                cursor.execute(sql)
            self.con.commit()
            df4 = pd.DataFrame(df3.values.T, index=df3.columns, columns=df3.index)
            return df4
        except Exception as e:
            print(e)
            self.F_rollback()

    def insertiterm(self,name,key,value):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            sql1 = "CREATE TABLE IF NOT EXISTS {0} ({1} VARCHAR(100) PRIMARY KEY, {2} VARCHAR(200), " \
                   "{3} VARCHAR(200) )".format(name,*key)
            cursor.execute(sql1)
            sql2 = "INSERT INTO {0} VALUES {1}".format(name,value)
            cursor.execute(sql2)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
    def showallitem(self,table):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            sql = "select * from {}".format(table)
            cursor.execute(sql)
            data =  cursor.fetchall() #使用fetchall函数以元组形式返回所有查询结果并打印出来
            #columnDes = cursor.description
            #columnNames = [columnDes[i][0] for i in range(len(columnDes))]
            #df = pd.DataFrame([list(i) for i in data], columns=columnNames)
            self.con.commit()
            return data
        except Exception as e:
            print(e)
            self.F_rollback()
    def query(self,table,para,signal,project):
        #print("signal",signal)
        df = pd.DataFrame()
        data1 = pd.DataFrame([[0]])
        data2 = pd.DataFrame([[0]])
        data3 = pd.DataFrame([[0]])
        data4 = pd.DataFrame([[0]])
        try:
            if not para:
                para = "seq>0"
            self.con.start_transaction()
            cursor = self.con.cursor()

            if signal[0]==1:
                sql = "select * from {0} where {1};".format(table,para)
            else:
                sql = "select project_db,PartName,DeutschName,Material,Thickness,Class,Weight,Amount,Cladding," \
                      "SetGroup,Supplier from {0} where {1};".format(table,para)
            #print(sql)
            cursor.execute(sql)
            data = cursor.fetchall()
            columnDes = cursor.description#获取连接对象的描述信息
            columnNames = [columnDes[i][0] for i in range(len(columnDes))]  # 获取列名
            df = pd.DataFrame([list(i) for i in data], columns=columnNames)
            if project:
                sumquerywhere = "({}) and (class regexp '单件')".format(project)
            else:
                sumquerywhere = "(class regexp '单件')"
            if signal[1]==1:
                sql1 = "select project_db,SUM(Amount) from {0} where {1} group by project_db;".format(table,para)
                cursor.execute(sql1)
                #print("sql1: ", sql1)
                data1 = cursor.fetchall()
                sql3 = "select project_db,SUM(Amount) from {0} where {1} group by project_db;".format(table,sumquerywhere)
                cursor.execute(sql3)
                #print("sql3: ", sql3)
                data3 = cursor.fetchall()
            if signal[2]==1:
                sql2 = "select project_db,SUM(Weight) from {0} where {1} group by project_db;".format(table,para)
                cursor.execute(sql2)
                #print("sql2: ", sql2)
                data2 = cursor.fetchall()
                sql4 = "select project_db,SUM(Weight) from {0} where {1} group by project_db;".format(table,sumquerywhere)
                cursor.execute(sql4)
                #print("sql4: ", sql4)
                data4 = cursor.fetchall()
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
        return (df,data1,data2,data3,data4)#data1-4 dataframe

    def query_sum(self,type,querywhere,db="project_db"):
        df = pd.DataFrame()
        data = pd.DataFrame([[0]])
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            sql1 = "select project_db,{0},SUM(Amount),SUM(Weight) from {1} where {2} and class='单件' group by {0} " \
                   "order by {0};".format(type,db,querywhere)
            #print(sql1)
            cursor.execute(sql1)
            data = cursor.fetchall()
            columnDes = cursor.description#获取连接对象的描述信息
            columnNames = [columnDes[i][0] for i in range(len(columnDes))]  # 获取列名
            df = pd.DataFrame([list(i) for i in data], columns=columnNames)
            #print(data)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
        return(df,data)
    def userdefine(self,sql):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            columnDes = cursor.description#获取连接对象的描述信息
            columnNames = [columnDes[i][0] for i in range(len(columnDes))]  # 获取列名
            df = pd.DataFrame([list(i) for i in data], columns=columnNames)
            self.con.commit()
            return df
        except Exception as e:
            print(e)
            self.F_rollback()
            return str(e)
    def deleteproject(self,project):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            sql="delete d,e from project_db d join project_list e on d.project_db=e.project_name " \
                "where d.project_db='{}';".format(project)
            cursor.execute(sql)
            e="{} has been deleted!".format(project)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
        return e
    def UserList(self):
        userlist = []
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            tablename = "UserList"
            sql = "CREATE TABLE IF NOT EXISTS {0} (UserName VARCHAR(200) PRIMARY KEY,"\
            "UserType ENUM('Admin','User','Visitor'));".format(tablename)
            #print("sql: ",sql)
            cursor.execute(sql)
            sql1 = "SELECT * From {0} WHERE UserType='Admin'".format("UserList")
            cursor.execute(sql1)
            #print("sql1： ",sql1)
            admin = cursor.fetchall()
            userlist.append(admin)
            sql2 = "SELECT * From {0} WHERE UserType='User'".format("UserList")
            cursor.execute(sql2)
            user = cursor.fetchall()
            userlist.append(user)
            sql3 = "SELECT * From {0} WHERE UserType='Visitor'".format("UserList")
            cursor.execute(sql3)
            visitor = cursor.fetchall()
            userlist.append(visitor)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
        return userlist
    def CreateUser(self,value):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            tablename = "UserList"
            sql = "CREATE TABLE IF NOT EXISTS {0} (UserName VARCHAR(200) PRIMARY KEY,"\
            "UserType ENUM('Admin','User','Visitor'));".format(tablename)
            cursor.execute(sql)

            sql3 = "create user '{0}'@'%' identified by '{1}'".format(value[0],value[2])
            #print(sql3)
            cursor.execute(sql3)
            if value[1] == "Admin":
                sql4 = "GRANT ALL ON  *.* TO '{}'@'%' with grant option;".format(value[0])
            if value[1] == "User":
                sql4 = "GRANT all privileges ON  biw.* TO '{}'@'%';".format(value[0])
            if value[1] == "Visitor":
                sql4 = "GRANT SELECT,execute ON  biw.* TO '{}'@'%';".format(value[0])
            #print(sql4)
            cursor.execute(sql4)
            sql2 = "INSERT INTO {0} VALUES {1}".format(tablename,value[:2])
            cursor.execute(sql2)
            sql5 = "FLUSH PRIVILEGES;"
            cursor.execute(sql5)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
    def DeleteUser(self,name):
        try:
            self.con.start_transaction()
            cursor = self.con.cursor()
            tablename = "UserList"
            sql1 = "drop user '{}'@'%';".format(name)
            cursor.execute(sql1)
            sql = "DELETE FROM {0} WHERE UserName='{1}'".format(tablename,name)
            cursor.execute(sql)
            sql2 = "FLUSH PRIVILEGES;"
            cursor.execute(sql2)
            self.con.commit()
        except Exception as e:
            print(e)
            self.F_rollback()
    def F_rollback(self):
        try:
            self.con.rollback()
        except:
            pass
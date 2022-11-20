#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Figure.py
# @Time      :2020/11/21 12:40
# @Author    :
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MyFigure(FigureCanvas):
    def __init__(self,width=30, height=20, dpi=100):
        #第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #第二步：在父类中激活Figure窗口
        super(MyFigure,self).__init__(self.fig) #此句必不可少，否则不能显示图形

    def plotbar(self,num,l,type): #num=[数量、重量],l=[项目名]
        self.axes1 = self.fig.add_subplot(111)
        self.axes1.clear()
        le = len(num)
        x_c = range(le)
        if le <5:
            x_c = range(5)
            l = l + ["" for j in range(5 - le)]
            num = num + [0 for i in range(5-le)]
        self.axes1.bar(x_c, num, tick_label=l, width=0.5)
        self.axes1.set_title(type)
        #print("b",num)
        for tick in self.axes1.get_xticklabels():
            tick.set_rotation(-15)
            #tick.set_fontsize(6)
        for i,j in zip(x_c,num):
            self.axes1.text(x=float(i)-0.2,y=float(j)+1.0,s="{}".format(j))
    def plotpie(self,num,sum,wei,sum_wei,label):
        le = len(num)
        i = 1
        j = i+le
        for item in zip(num,sum,label):

            axis=self.fig.add_subplot(2,le,i)
            if i == 1:
                axis.set_ylabel("number")
            axis.pie(list(item[:2]),autopct='%3.1f%%',explode=[0.05,0])
            axis.text(x=-1, y=1.5, s=item[2])
            i += 1
            # axis.set_xticks([])
            # axis.set_yticks([])
            # axis.get_xaxis().set_visible(False)
            # axis.get_yaxis().set_visible(False)
            #axis.set_ylabel(type)
        for item in zip(wei,sum_wei):
            axis=self.fig.add_subplot(2,le,j)
            if j == le+1:
                axis.set_ylabel("weight")
            axis.pie(list(item[:2]),autopct='%3.1f%%',explode=[0.05,0])
            j += 1

        #axis.set_title(type)
        #axis.text(x=0.2, y=1, s=type)
    def plotpiesum(self,number,weight,label):
        try:
            axis1 = self.fig.add_subplot(1, 2, 1)
            axis1.pie(number, autopct='%3.1f%%',labels=label)
            axis1.text(x=-0.3, y=1.3, s="number")
            axis2 = self.fig.add_subplot(1, 2, 2)
            axis2.pie(weight, autopct='%3.1f%%',labels=label)
            axis2.text(x=-0.3, y=1.3, s="weight")
        except Exception as e:
            print(e)


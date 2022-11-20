#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :TableViewModel.py
# @Time      :2020/10/3 14:57
# @Author    :

from PyQt5.QtCore import QAbstractTableModel,Qt

class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data
        self.sortOrder = Qt.AscendingOrder

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None

    # def sort(self, Ncol, order):
    #     """Sort table by given column number.
    #     """
    #     self.layoutAboutToBeChanged.emit()
    #     self.arraydata = sorted(self._data, key=operator.itemgetter(Ncol))
    #     if order == Qt.DescendingOrder:
    #         self.arraydata.reverse()
    #     self.layoutChanged.emit()
    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(self._data.columns[Ncol], ascending=not order)
            self.layoutChanged.emit()
        except Exception as e:
            print(e)
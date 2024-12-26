import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
import pandas as pd

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, labels:list):
        super(TableModel, self).__init__()
        self._data          = data
        self.hheaders    = labels

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return 'Column {}'.format(section + 1)
        return super().headerData(section, orientation, role)

    def headerData(self, section, orientation, role):           # <<<<<<<<<<<<<<< NEW DEF
        # row and column headers
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.hheaders[section]
        return 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        df = pd.read_csv('Generator_database.csv')
        data = df.values.tolist()
        # Main Widget and Layout
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout(main_widget)

        def add_widget(layout:QtWidgets,widget:QtWidgets,label:str = None):
            hbox = QtWidgets.QHBoxLayout()
            if label != None:
                label = QtWidgets.QLabel(label)
                hbox.addWidget(label)
            hbox.addWidget(widget)
            layout.addLayout(hbox)

        table_layout = QtWidgets.QVBoxLayout()
        self.table = QtWidgets.QTableView()
        self.model = TableModel(data,df.columns.to_list())
        self.table.setModel(self.model)
        table_layout.addWidget(self.table)

        vlayout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel('New Label')
        vlayout.addWidget(label)

        text_edit = QtWidgets.QTextEdit()
        vlayout.addWidget(text_edit)

        main_layout.addLayout(vlayout)
        main_layout.addLayout(table_layout,3)
        





if __name__ == '__main__':
    app     = QtWidgets.QApplication(sys.argv)
    window  = MainWindow()
    window.show()
    app.exec()
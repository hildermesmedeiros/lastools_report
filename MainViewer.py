import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import traceback

import pandas as pd

#import pdb
class MainViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LasInfo viewer")
        self.setGeometry(350,150,500,400)
        self.fileIndex = 0
        self.lasIndex = 0
        self.lasUrls = ([],'')
        self.urls = ([],'')
        self.file = []
        self.numberFiles = 0
        self.numberLasFiles = 0
        self.dataFrame = pd.DataFrame(
            columns=["X", "Y", "Z", "intensity", "return_number", "number_of_returns", "edge_of_flight_line",
                     "scan_direction_flag", "classification", "scan_angle_rank", "user_data", "point_source_ID",
                     "gps_time", "path"])

        self.dataFrame = self.dataFrame.astype(
            dtype={"X": "float64", "Y": "float64", "Z": "float64", "intensity": "int64", "return_number": "int64",
                   "number_of_returns": "int64", "edge_of_flight_line": "int64",
                   "scan_direction_flag": "int64", "classification": "int64", "scan_angle_rank": "float64",
                   "user_data": "int64", "point_source_ID": "int64",
                   "gps_time": "float64", "path": "str"})
        self.clip = QApplication.clipboard()

        self.UI()
        self.showMaximized()

    def UI(self):
        self.toolbar()
        self.tabWidget()
        self.tab1Widget()
        self.tab2Widget()
        self.layouts()
        self.display_table()

    def toolbar(self):
        self.tb = self.addToolBar("teste")
        self.tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        ############ First button ######################
        self.lastFile = QAction(self,text="Voltar")
        self.tb.addAction(self.lastFile)
        self.lastFile.triggered.connect(self.lastFileAct)
        self.tb.addSeparator()
        ############ Second button #####################
        self.nextFile = QAction(self,text="Avancar")
        self.tb.addAction(self.nextFile)
        self.nextFile.triggered.connect(self.nextFileAct)
        self.tb.addSeparator()
        ############ Third button #####################
        self.open = QAction(self,text="Abri arquivo(s) de relatorio(s)")
        self.tb.addAction(self.open)
        self.open.triggered.connect(self.openFile)
        self.tb.addSeparator()
        ############ Fourth button #####################
        self.lasInfo = QAction(self,text="Run Lasinfo")
        self.tb.addAction(self.lasInfo)
        self.lasInfo.triggered.connect(self.runLasinfo)
        self.tb.addSeparator()

    def tabWidget(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1=QWidget()
        self.tab2=QWidget()
        self.tabs.addTab(self.tab1,"Las Info")
        self.tabs.addTab(self.tab2,"Las Statics")

    def tab1Widget(self):
        ############ tab1 widget ############
        font = QFont("Times", 18)
        self.txtViewer = QTextEdit(self)

    def tab2Widget(self):
        ########### tab2 widget #############

        self.table = QTableWidget()
        self.table.setColumnCount(14)
        for i in range(14):
            self.table.setHorizontalHeaderItem(i, QTableWidgetItem(self.dataFrame.keys()[i]))
            if i>=0 and i<3:
                self.table.setColumnWidth(i, 80)
            elif i == 12:
                self.table.setColumnWidth(12, 150)
            else:
                self.table.setColumnWidth(i, len(self.dataFrame.keys()[i]) * 9)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def keyPressEvent(self, e):
        #https://stackoverflow.com/questions/24971305/copy-pyqt-table-selection-including-column-and-row-headers
        if (e.modifiers() & Qt.ControlModifier):
            selected = self.table.selectedRanges()

            if e.key() == Qt.Key_C: #copy
                s = '\t'+"\t".join([str(self.table.horizontalHeaderItem(i).text()) for i in range(selected[0].leftColumn(), selected[0].rightColumn()+1)])
                s = s + '\n'

                for r in range(selected[0].topRow(), selected[0].bottomRow()+1):
                    s += self.table.verticalHeaderItem(r).text() + '\t'
                    for c in range(selected[0].leftColumn(), selected[0].rightColumn()+1):
                        try:
                            s += str(self.table.item(r,c).text()) + "\t"
                        except AttributeError:
                            s += "\t"
                    s = s[:-1] + "\n" #eliminate last '\t'
                self.clip.setText(s)

    def layouts(self):
        ############## tab1 Layout#########
        self.tab1_mainLayout = QHBoxLayout()
        self.tab1_insideLayout = QVBoxLayout()

        ##### adding layouts  to tab1 ####
        self.tab1_insideLayout.addWidget(self.txtViewer)
        self.tab1_mainLayout.addLayout(self.tab1_insideLayout)
        self.tab1.setLayout(self.tab1_mainLayout)

        ############## tab2 Layout#########
        self.tab2_mainLayout = QHBoxLayout()
        self.tab2_insideLayout = QVBoxLayout()

        #### adding layouts to tab2 #####
        self.tab2_insideLayout.addWidget(self.table)
        self.tab2_mainLayout.addLayout(self.tab2_insideLayout)
        self.tab2.setLayout(self.tab2_mainLayout)


    def checkEmpty(self, url =([],"")):
        "Check if givel list contais a list of urls and returns True if it is empty, or False if it is not."
        fileList, fileType = url
        if fileList == []:
            return True
        else:
            return False

    def openFile(self):
        try:
            emptyOld = self.checkEmpty(self.urls)

            self.urls = QFileDialog.getOpenFileNames(self, "Escolha o arquivo", "", "All Files(*);;*txt")
            empty = self.checkEmpty(self.urls)
            if empty is False and emptyOld is True:
                fileList, fileType = self.urls
                self.getTable(fileList)
                fileUrl = fileList[self.fileIndex]
                self.numberFiles = len(fileList) - 1
                self.file = open(fileUrl, 'r')
                content = self.file.read()
                self.txtViewer.setText(content)
                self.display_table()
            elif empty is False and emptyOld is False:
                fileList, fileType = self.urls
                self.dataFrame.drop(self.dataFrame.index, inplace=True)
                self.getTable(fileList)
                self.numberFiles = len(fileList) - 1
                self.updateTxt()
                self.display_table()
            else:
                pass
        except Exception as e:
            print(traceback.format_exc())

    def updateTxt(self):
        self.file.close()
        fileList, fileType = self.urls
        fileUrl = fileList[self.fileIndex]
        if fileUrl:
            self.file = open(fileUrl, 'r')
            content = self.file.read()
            self.txtViewer.setText(content)
            self.txtViewer.update()

    def nextFileAct(self):
        try:
            if self.tab1 is self.tabs.currentWidget():
                empty = self.checkEmpty(self.urls)
                fileList, fileType = self.urls
                if empty is False:
                    if self.fileIndex < self.numberFiles:
                        self.fileIndex = self.fileIndex + 1
                        self.updateTxt()
        except Exception as e:
            print(traceback.format_exc())

    def lastFileAct(self):
        try:
            if self.tab1 is self.tabs.currentWidget():
                empty = self.checkEmpty(self.urls)
                fileList, fileType = self.urls
                if empty is False:
                    if self.fileIndex > 0:
                        self.fileIndex = self.fileIndex - 1
                        self.updateTxt()
        except Exception as e:
            print(traceback.format_exc())

    def getTable(self, fileList=([],"")):
        empty = self.checkEmpty(self.urls)
        if empty is False:
            for file in fileList:
                data = pd.read_csv(file, skiprows=57, nrows=13, header=None, delim_whitespace=True,
                                   names=["min", "max"])
                data = data.T
                data.insert(loc=13 ,column='path', value=file)
                self.dataFrame = self.dataFrame.append(data, ignore_index=True)
                self.dataFrame = self.dataFrame.astype(
                    dtype={"X": "float64", "Y": "float64", "Z": "float64", "intensity": "int64",
                           "return_number": "int64",
                           "number_of_returns": "int64", "edge_of_flight_line": "int64",
                           "scan_direction_flag": "int64", "classification": "int64", "scan_angle_rank": "float64",
                           "user_data": "int64", "point_source_ID": "int64",
                           "gps_time": "float64", "path": "str"})
                #print(self.dataFrame)


    def display_table(self):
        for i in reversed(range(self.table.rowCount())):
            self.table.removeRow(i)
        string = ''
        i = 0
        for index, _ in self.dataFrame.iterrows():
            self.table.insertRow(index)

            if index == 0:
                label = QTableWidgetItem("0 Min")
                self.table.setVerticalHeaderItem(index, label)
                string = str(index - i)
            elif (index % 2) == 0:
                i = i + 1
                label = QTableWidgetItem(str(index - i) + ' Min')
                self.table.setVerticalHeaderItem(index, label)
                string = str(index - i)
            else:
                label = QTableWidgetItem(string + ' Max')
                self.table.setVerticalHeaderItem(index, label)

            for column in range(14):
                self.table.setItem(index, column, QTableWidgetItem(str(self.dataFrame.iloc[index, column])))


    def runLasinfo(self):
        try:
            self.lasUrls = QFileDialog.getOpenFileNames(self, "Escolha o(s) Las ou o(s) Laz", "", "All Files(*);;*las;;*laz")
            empty = self.checkEmpty(self.lasUrls)
            if empty is False:
                fileList, fileType = self.lasUrls
                self.numberLasFiles = len(fileList) - 1
                for fileUrl in fileList:
                    os.system(".\\LAStools\\bin\\lasinfo.exe -i \"" + fileUrl + "\" -otxt -odix \"_report\"")
                msg = QMessageBox.information(self, "Relatório Feito", "Arquivo(s) de relatório salvo(s)")
            else:
                pass
        except Exception as e:
            print(traceback.format_exc())

def main():
    App=QApplication(sys.argv)
    window = MainViewer()
    sys.exit(App.exec_())

if __name__ == '__main__':
    main()